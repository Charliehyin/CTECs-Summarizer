def load_config():
    config = {}
    try:
        with open('assistant_config.txt', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key] = value
    except Exception as e:
        print("Error reading configuration:", e)
    return config
