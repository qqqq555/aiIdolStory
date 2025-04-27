# load_env.py
import os

def load_env_file(env_file='.env'):
    """
    從.env文件加載環境變量
    """
    if os.path.exists(env_file):
        print(f"正在從{env_file}加載環境變量...")
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳過空行和註釋
                if not line or line.startswith('#'):
                    continue
                
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
        print("環境變量加載完成")
    else:
        print(f"警告: {env_file}文件不存在，使用默認值或現有環境變量")

if __name__ == "__main__":
    # 如果直接運行此腳本，將加載環境變量
    load_env_file()