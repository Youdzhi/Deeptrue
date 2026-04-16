from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import cv2
import os
from datetime import datetime
import glob
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tiktok_down import TikTokDownloader
import base64
import re

# Load environment variables
load_dotenv()


def interpolate_values(array):
    """Interpolate None values in array using linear interpolation"""
    n = len(array)
    if n == 0:
        return array
    
    # Find all known value indices
    known_indices = [i for i in range(n) if array[i] is not None]
    
    if len(known_indices) == 0:
        # No known values, fill with 50
        return [50] * n
    
    # Fill values before first known value
    for i in range(known_indices[0]):
        array[i] = array[known_indices[0]]
    
    # Fill values between known indices using linear interpolation
    for k in range(len(known_indices) - 1):
        start_idx = known_indices[k]
        end_idx = known_indices[k + 1]
        start_val = array[start_idx]
        end_val = array[end_idx]
        
        # Linear interpolation
        for i in range(start_idx + 1, end_idx):
            if array[i] is None:
                t = (i - start_idx) / (end_idx - start_idx)
                array[i] = int(start_val + t * (end_val - start_val))
    
    # Fill values after last known value
    last_idx = known_indices[-1]
    for i in range(last_idx + 1, n):
        if array[i] is None:
            array[i] = array[last_idx]
    
    return array


def merge_values(base_array, new_values, start_idx, end_idx):
    """Merge new values into base array using interpolation/averaging at overlaps"""
    for idx in range(start_idx, end_idx):
        if base_array[idx] is None:
            base_array[idx] = new_values[idx - start_idx]
        else:
            # Interpolate between existing and new value
            existing = base_array[idx]
            new = new_values[idx - start_idx]
            base_array[idx] = int((existing + new) / 2)


def encode_image_to_base64(image_path):
    """Encode an image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        return None


def extract_ai_answer(resp: dict) -> str:
    """Extract AI answer from Pollinations API response"""
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return "Ошибка."


def generate_llm_explanation(video_data, frame_files, ai_generated_array, individual_frames, mean_percentage):
    """Generate detailed explanation using Pollinations API"""
    try:
        pollinations_api_url = "https://text.pollinations.ai/openai"
        pollinations_api_token = os.getenv('POLLINATIONS_API')
        
        if not pollinations_api_url or not pollinations_api_token:
            return "LLM explanation unavailable: Pollinations API URL or token not found in .env file. Required: wTbvlpd-P5J0_9Wx and NEUROYDZ_TOKEN"
        
        # Prepare frame information - encode key frames as base64 images
        frame_samples = []
        sample_indices = []
        
        # Get frames that were directly checked (limit to avoid huge prompts)
        max_samples = min(5, len(individual_frames))
        for frame_info in individual_frames[:max_samples]:
            idx = frame_info['frame_index']
            if idx < len(frame_files):
                frame_path = frame_files[idx]
                frame_base64 = encode_image_to_base64(frame_path)
                if frame_base64:
                    frame_samples.append({
                        'index': idx,
                        'name': frame_info['frame_name'],
                        'ai_percentage': frame_info['ai_generated_percentage'],
                        'image_base64': frame_base64
                    })
                    sample_indices.append(idx)
        
        # Also include frames with highest and lowest AI percentages
        if ai_generated_array:
            max_val = max(ai_generated_array)
            min_val = min(ai_generated_array)
            max_idx = ai_generated_array.index(max_val)
            min_idx = ai_generated_array.index(min_val)
            
            for idx in [max_idx, min_idx]:
                if idx not in sample_indices and idx < len(frame_files) and len(frame_samples) < 7:
                    frame_path = frame_files[idx]
                    frame_base64 = encode_image_to_base64(frame_path)
                    if frame_base64:
                        frame_samples.append({
                            'index': idx,
                            'name': f"frame_{idx:05d}.jpg",
                            'ai_percentage': ai_generated_array[idx],
                            'image_base64': frame_base64
                        })
                        sample_indices.append(idx)
        
        # Create comprehensive prompt with all data
        array_summary = f"First 30 frames: {ai_generated_array[:30]}" if len(ai_generated_array) > 30 else str(ai_generated_array)
        array_stats = {
            'total_frames': len(ai_generated_array),
            'max_percentage': max(ai_generated_array) if ai_generated_array else 0,
            'min_percentage': min(ai_generated_array) if ai_generated_array else 0,
            'frames_above_50': sum(1 for p in ai_generated_array if p >= 50) if ai_generated_array else 0,
            'frames_below_50': sum(1 for p in ai_generated_array if p < 50) if ai_generated_array else 0
        }
        
        # Build prompt with embedded images
        prompt_parts = [
            "Analyze this video's AI generation detection results and provide a detailed explanation.",
            "",
            "VIDEO ANALYSIS SUMMARY:",
            f"- Total frames analyzed: {video_data.get('total_frames', 0)}",
            f"- Frames directly checked via API: {video_data.get('frames_checked', 0)}",
            f"- Mean AI generation percentage: {mean_percentage:.2f}%",
            "",
            "AI GENERATION STATISTICS:",
            json.dumps(array_stats, indent=2),
            "",
            f"AI GENERATION PERCENTAGES ARRAY (0-100 scale, {len(ai_generated_array)} frames total):",
            array_summary,
            "",
            "INDIVIDUALLY CHECKED FRAMES (directly analyzed by AI detection API):",
            json.dumps(individual_frames, indent=2),
        ]
        
        # Add frame images in the prompt
        if frame_samples:
            prompt_parts.extend([
                "",
                "KEY FRAME IMAGES:",
                "Below are base64-encoded images of important frames from the video."
            ])
            for i, sample in enumerate(frame_samples, 1):
                prompt_parts.append(
                    f"\nFrame {i} (Index {sample['index']}, {sample['name']}, AI: {sample['ai_percentage']}%):"
                )
                prompt_parts.append(f"[IMAGE_DATA: {sample['image_base64']}]")
        
        prompt_parts.extend([
            "",
            "Please provide a comprehensive detailed explanation covering:",
            "1. Overall assessment: Is this video likely AI-generated, human-created, or mixed?",
            "2. Analysis of the AI percentage distribution across all frames",
            "3. Notable patterns: Are there sections with consistently high/low AI scores?",
            "4. Interpretation: What does the mean percentage of {:.2f}% mean practically?".format(mean_percentage),
            "5. Frame analysis: Comment on the specific frames that were directly checked",
            "6. Visual analysis: Describe what you see in the provided frame images",
            "7. Confidence assessment: How reliable are these detection results?",
            "8. Practical implications: What should users know about this video?",
            "",
            "Be thorough, technical but accessible, and provide actionable insights."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        # Remove image data markers from prompt (images are too large for text-only API)
        text_prompt = re.sub(r'\[IMAGE_DATA:.*?\]', '', prompt)
        # Add note about images if we had them
        if frame_samples:
            image_note = f"\n\nNote: {len(frame_samples)} key frame images were analyzed but cannot be included in text format. Analysis is based on frame indices and AI detection scores."
            text_prompt = text_prompt + image_note
        
        # Call Pollinations API using the provided format
        print("Call started")
        
        link = pollinations_api_url
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {pollinations_api_token}"
        }
        payload = {
            "model": "openai",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert video analysis assistant. Provide detailed, technical explanations about AI-generated content detection in videos."
                },
                {
                    "role": "user",
                    "content": text_prompt
                }
            ]
        }
        
        response = requests.post(link, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            resp = response.json()
            explanation = extract_ai_answer(resp)
            if explanation and explanation != "Ошибка.":
                return explanation
            else:
                return f"LLM explanation unavailable: Could not extract answer from response. Response: {str(resp)[:200]}"
        else:
            return f"LLM explanation unavailable: API returned status {response.status_code}. Response: {response.text[:300]}"
    
    except requests.exceptions.Timeout:
        return "LLM explanation unavailable: Request timeout. The analysis took too long."
    except requests.exceptions.RequestException as e:
        return f"LLM explanation unavailable: Request error - {str(e)}"
    except Exception as e:
        return f"LLM explanation unavailable: Error - {str(e)}"


@csrf_exempt
def check_video(request):
    """Django endpoint to check video frames for AI generation"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Only POST method allowed'}, status=405)
        
        # Get parameters from request
        data = json.loads(request.body) if request.body else {}
        video_url = data.get('video_url', 'https://vt.tiktok.com/ZSyMN8Q28/')
        userid = data.get('userid', '1234567890')
        user_path = userid + '_tt'
        
        # Initialize downloader
        downloader = TikTokDownloader(save_path=user_path)
        
        # Download video
        downloader.download_video(video_url)
        
        # Find downloaded .mp4
        video_files = glob.glob(os.path.join(user_path, "*.mp4"))
        if not video_files:
            return JsonResponse({'error': 'Видео не найдено после загрузки'}, status=404)
        
        video_path = video_files[0]
        
        # Create folder for frames
        folder_name = f"tiktok_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        frames_folder = os.path.join(user_path, folder_name)
        os.makedirs(frames_folder, exist_ok=True)
        
        # Read video and extract frames
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Save every 10th frame
            if frame_count % 10 == 0:
                frame_file = os.path.join(frames_folder, f"frame_{saved_count:05d}.jpg")
                cv2.imwrite(frame_file, frame)
                saved_count += 1
            
            frame_count += 1
        
        cap.release()
        
        # Get API keys
        api_user = os.getenv('SIGHTENGINE_API_USER')
        api_secret = os.getenv('SIGHTENGINE_API_SECRET')
        
        if not api_user or not api_secret:
            return JsonResponse({
                'error': 'API ключи не найдены в .env файле. Убедитесь, что SIGHTENGINE_API_USER и SIGHTENGINE_API_SECRET установлены.'
            }, status=500)
        
        # Find all frames
        frame_files = sorted(glob.glob(os.path.join(frames_folder, "frame_*.jpg")))
        total_frames = len(frame_files)
        
        if total_frames == 0:
            return JsonResponse({'error': 'Кадры не найдены для проверки'}, status=404)
        
        # Create empty array for results
        ai_generated_array = [None] * total_frames
        
        # Determine which frames to check (max 10 API calls)
        max_api_calls = min(10, total_frames)
        step = max(1, total_frames // max_api_calls)
        
        # Select indices to check
        frames_to_check = []
        for i in range(0, total_frames, step):
            frames_to_check.append(i)
            if len(frames_to_check) >= max_api_calls:
                break
        
        # Add last frame if we have space
        if len(frames_to_check) < max_api_calls and total_frames > 0:
            frames_to_check.append(total_frames - 1)
        
        # Remove duplicates and sort
        frames_to_check = sorted(list(set(frames_to_check)))
        
        # Function to check one frame
        def check_frame_ai_generated(frame_index, frame_path):
            """Check one frame for AI generation via Sightengine API"""
            try:
                with open(frame_path, 'rb') as f:
                    files = {'media': f}
                    data = {
                        'models': 'genai',
                        'api_user': api_user,
                        'api_secret': api_secret
                    }
                    response = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=data)
                    response.raise_for_status()
                    result = response.json()
                    
                    # Get AI generation percentage (0-1, convert to 0-100)
                    ai_score = result.get('type', {}).get('ai_generated', 0.0)
                    percentage = int(ai_score * 100)
                    
                    return frame_index, percentage
            except Exception as e:
                return frame_index, 50  # Default 50 on error
        
        # Check frames in parallel
        results = []
        individual_frames = []
        with ThreadPoolExecutor(max_workers=max_api_calls) as executor:
            futures = {
                executor.submit(check_frame_ai_generated, idx, frame_files[idx]): idx 
                for idx in frames_to_check
            }
            
            for future in as_completed(futures):
                frame_index, percentage = future.result()
                results.append((frame_index, percentage))
                individual_frames.append({
                    'frame_index': frame_index,
                    'frame_name': f"frame_{frame_index:05d}.jpg",
                    'ai_generated_percentage': percentage
                })
        
        # Sort results by index
        results.sort(key=lambda x: x[0])
        individual_frames.sort(key=lambda x: x['frame_index'])
        
        # Apply labeling logic with percentages
        for frame_index, percentage in results:
            if percentage >= 50:  # AI-generated (>=50%)
                # Label 100 frames: 50 left, 50 right, using actual percentage
                start_idx = max(0, frame_index - 50)
                end_idx = min(total_frames, frame_index + 51)
                
                # Create array with percentage values for this range
                # Use percentage at center, fade linearly to edges
                center_local_idx = frame_index - start_idx
                
                for idx in range(start_idx, end_idx):
                    local_idx = idx - start_idx
                    # Distance from center frame
                    distance = abs(local_idx - center_local_idx)
                    # Fade percentage linearly from center (full) to edges (0)
                    # Max distance is 50, fade over that range
                    fade_factor = max(0, 1 - (distance / 50))
                    value = int(percentage * fade_factor)
                    
                    if ai_generated_array[idx] is None:
                        ai_generated_array[idx] = value
                    else:
                        # Intersection - interpolate between existing and new value
                        existing = ai_generated_array[idx]
                        # Weight: closer to center = more influence from new value
                        weight = fade_factor
                        ai_generated_array[idx] = int(existing * (1 - weight) + value * weight)
            else:  # Not AI-generated (<50%)
                # Label 40 frames: 20 left, 20 right, as 0
                start_idx = max(0, frame_index - 20)
                end_idx = min(total_frames, frame_index + 21)
                
                center_local_idx = frame_index - start_idx
                
                for idx in range(start_idx, end_idx):
                    local_idx = idx - start_idx
                    distance = abs(local_idx - center_local_idx)
                    # Fade from center to edges
                    fade_factor = max(0, 1 - (distance / 20))
                    value = int(0 * fade_factor)  # Always 0, but using fade_factor for consistency
                    
                    if ai_generated_array[idx] is None:
                        ai_generated_array[idx] = 0
                    else:
                        # Intersection - interpolate (existing value fades towards 0)
                        existing = ai_generated_array[idx]
                        # Weight: closer to center = more influence towards 0
                        weight = fade_factor * 0.5  # Less aggressive than AI case
                        ai_generated_array[idx] = int(existing * (1 - weight) + 0 * weight)
        
        # Interpolate remaining None values
        ai_generated_array = interpolate_values(ai_generated_array)
        
        # Calculate mean value
        mean_value = sum(ai_generated_array) / len(ai_generated_array) if ai_generated_array else 0
        
        # Prepare video data for LLM explanation
        video_data = {
            'total_frames': total_frames,
            'frames_checked': len(frames_to_check),
            'api_calls_made': len(frames_to_check),
            'video_path': video_path,
            'frames_folder': frames_folder
        }
        
        # Generate LLM explanation
        llm_explanation = generate_llm_explanation(
            video_data,
            frame_files,
            ai_generated_array,
            individual_frames,
            mean_value
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'total_frames': total_frames,
            'frames_checked': len(frames_to_check),
            'api_calls_made': len(frames_to_check),
            'ai_generated_array': ai_generated_array,
            'mean_percentage': round(mean_value, 2),
            'individual_frames': individual_frames,
            'frames_folder': frames_folder,
            'video_path': video_path,
            'llm_explanation': llm_explanation
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

