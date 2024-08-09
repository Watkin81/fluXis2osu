# --------------------------- #
# fluXis to Osz map converter #
# v1.0                        #
# --------------------------- #

# -------------------------------------------- #
# Change these at your leisure or don't idc
input_file_path = r"<Input Path to .fsc File>"
output_dir = r"<Output Path for The .osz File>"
# -------------------------------------------- #

import json
import os
import zipfile

def find_file_in_directory(directory, filename):
    """Find a file in a given directory."""
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

def convert_file(input_file_path, output_dir):
    if not os.path.isfile(input_file_path):
        print(f"Error: Input file {input_file_path} does not exist.")
        return

    encodings = ['utf-8', 'utf-16', 'latin-1']
    data = None
    for encoding in encodings:
        try:
            with open(input_file_path, 'r', encoding=encoding) as input_file:
                data = json.load(input_file)
            break
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Attempt with encoding {encoding} failed. Error: {e}")
    if data is None:
        print("Error: Failed to decode JSON with all attempted encodings.")
        return

    metadata = data.get("Metadata", {})
    title = metadata.get('Title', 'Untitled Map')

    audio_file_name = data.get('AudioFile', 'audio.mp3')
    background_file_name = data.get('BackgroundFile', 'unknownBackground.jpg')
    
    fsc_directory = os.path.dirname(input_file_path)
    
    audio_file_path = find_file_in_directory(fsc_directory, audio_file_name)
    background_file_path = find_file_in_directory(fsc_directory, background_file_name)
    
    if audio_file_path is None:
        print(f"Error: Audio file {audio_file_name} not found.")
    if background_file_path is None:
        print(f"Error: Background file {background_file_name} not found.")

    osu_file_path = os.path.join(output_dir, f'{title}.osu')
    zip_file_path = os.path.join(output_dir, f'{title}.osz')
    
    with open(osu_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write("osu file format v14\n\n")
        
        # [General] Section
        output_file.write("[General]\n")
        output_file.write(f"AudioFilename: {os.path.basename(audio_file_path) if audio_file_path else 'audio.mp3'}\n")
        output_file.write("AudioLeadIn: 0\n")
        output_file.write(f"PreviewTime: {metadata.get('PreviewTime', '-1')}\n")
        output_file.write("Countdown: 1\n")
        output_file.write("SampleSet: Normal\n")
        output_file.write("StackLeniency: 0.7\n")
        output_file.write("Mode: 3\n")
        output_file.write("LetterboxInBreaks: 0\n")
        output_file.write("SpecialStyle: 0\n")
        output_file.write("WidescreenStoryboard: 0\n\n")
        
        # [Editor] Section
        output_file.write("[Editor]\n")
        output_file.write("DistanceSpacing: 1\n")
        output_file.write("BeatDivisor: 4\n")
        output_file.write("GridSize: 4\n")
        output_file.write("TimelineZoom: 1\n\n")
        
        # [Metadata] Section
        output_file.write("[Metadata]\n")
        output_file.write(f"Title:{title}\n")
        output_file.write(f"TitleUnicode:{metadata.get('TitleUnicode', 'unknown')}\n")
        output_file.write(f"Artist:{metadata.get('Artist', 'Unknown Artist')}\n")
        output_file.write(f"ArtistUnicode:{metadata.get('ArtistUnicode', 'unknown')}\n")
        output_file.write(f"Creator:{metadata.get('Mapper', 'Unknown Mapper')}\n")
        output_file.write(f"Version:{metadata.get('Difficulty', 'Unknown Difficulty')}\n")
        output_file.write(f"Source:{metadata.get('Source', 'unknown')}\n")
        output_file.write(f"Tags:{metadata.get('Tags', '')}\n")
        output_file.write(f"BeatmapID:0\n")
        output_file.write(f"BeatmapSetID:-1\n\n")
        
        # [Difficulty] Section
        output_file.write("[Difficulty]\n")
        output_file.write(f"HPDrainRate:{data.get('AccuracyDifficulty', 5)}\n")
        output_file.write(f"CircleSize:{data.get('CircleSize', 4)}\n")
        output_file.write(f"OverallDifficulty:{data.get('OverallDifficulty', 5)}\n")
        output_file.write(f"ApproachRate:{data.get('ApproachRate', 5)}\n")
        output_file.write(f"SliderMultiplier:1.4\n")
        output_file.write(f"SliderTickRate:1\n\n")
        
        # [Events] Section
        output_file.write("[Events]\n")
        if background_file_path:
            output_file.write(f"0,0,\"{os.path.basename(background_file_path)}\",0,0\n")
        output_file.write("\n")
        
        # [TimingPoints] Section
        output_file.write("[TimingPoints]\n")
        for tp in data.get("TimingPoints", []):
            time = int(tp["time"])
            bpm = tp.get("bpm", 60.0)
            signature = tp.get("signature", 4)
            output_file.write(f"{time},{60000 / bpm},{signature},1,0,100,1,0\n")
        output_file.write("\n")
        
        # [HitObjects] Section
        output_file.write("[HitObjects]\n")
        for obj in data.get("HitObjects", []):
            x = 64 + (obj["lane"] - 1) * 128
            y = 192
            time = int(obj["time"])
            holdtime = int(obj.get("holdtime", 0))
            
            if holdtime:  # LN
                type_flag = 128  # Slider
                end_time = time + holdtime
                output_file.write(f"{x},{y},{time},{type_flag},0,{end_time}:0:0:0:0:\n")
            else:  # Circle
                type_flag = 1  # Circle
                output_file.write(f"{x},{y},{time},{type_flag},0\n")

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip_file:
        files_to_zip = [(osu_file_path, os.path.basename(osu_file_path))]
        
        if audio_file_path:
            files_to_zip.append((audio_file_path, os.path.basename(audio_file_path)))
        
        if background_file_path:
            files_to_zip.append((background_file_path, os.path.basename(background_file_path)))
        
        for file_path, arcname in files_to_zip:
            try:
                print(f"Adding {file_path} to ZIP archive...")
                zip_file.write(file_path, arcname)
            except Exception as e:
                print(f"Error adding {file_path} to ZIP archive: {e}")

    if os.path.isfile(osu_file_path):
        os.remove(osu_file_path)
        print(f"Deleted temporary file {osu_file_path}")

    print(f"Conversion complete. Map saved to {zip_file_path}.")

convert_file(input_file_path, output_dir)