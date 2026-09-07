# custom exception for log lines that do not match expected format
class InvalidLogFormat(Exception):
    pass

# parses a single raw log line into a dictionary with timestamp, level, and message
def parse_log_line(line):
    line = line.strip()
    if not line:
        raise InvalidLogFormat("Empty line")
        
    parts = line.split(" | ")
    if len(parts) != 3:
        raise InvalidLogFormat(f"Expected 3 parts separated by ' | ', got {len(parts)}: '{line}'")
        
    timestamp, level, message = parts
    return {
        "timestamp": timestamp.strip(),
        "level": level.strip(),
        "message": message.strip()
    }

# reads a log file line by line, catching malformed lines without crashing
def parse_log_file(filepath):
    valid_logs = []
    skipped_count = 0
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                entry = parse_log_line(line)
                valid_logs.append(entry)
            except InvalidLogFormat as err:
                skipped_count = skipped_count + 1
                print(f"[Warning] Line {line_num} skipped -> {err}")
                
    return valid_logs, skipped_count

if __name__ == "__main__":
    log_file = "sample.log"
    print(f"Reading log file: {log_file}\n")
    
    parsed_entries, errors = parse_log_file(log_file)
    
    print(f"\n--- Summary ---")
    print(f"Successfully parsed: {len(parsed_entries)} lines")
    print(f"Skipped bad lines:   {errors} lines")
    
    print("\n--- Parsed Entries ---")
    for item in parsed_entries:
        print(f"[{item['timestamp']}] ({item['level']}) {item['message']}")
