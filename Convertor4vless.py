# 使用说明：
#   1.在V2Ray订阅地址中填入Okgg的订阅地址即可直接运行即可得到配置文件。


import base64
import requests
from urllib.parse import quote, unquote

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

# V2Ray 订阅地址
subscription_url = ""

# 请求订阅链接，获取节点信息
response = requests.get(subscription_url)

# Base64编码的字符串
base64_string = response.text

# decode base64
decoded_urldata = base64.b64decode(base64_string)
# decode url
decoded_data = unquote(decoded_urldata)

# 自定义解析器 TODO 提取 chatgpt相关节点
def custom_okgg_yaml_parser_2023_v1(data, fun_param):
    
    parsed_data = []
    node_name_data_list = []
    
    lines = data.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("ss://"):
            continue
        
        # 处理vless + h2 的情况
        elif line.startswith("vless://") and ("h2" in line):
            info = line[8:]
            parts = info.split("?", 1)
            
            params_dict = {}
            if len(parts) > 1:
                params = parts[1].split("&")
                for param in params:
                    key, value = param.split("=")
                    params_dict[key] = value
                    
                    
            host_port = parts[0].split("@")[1].split(":")
            if len(host_port) > 1:
                port = int(host_port[-1])
            else:
                port = None
                
            item = {
                "name": params_dict.get("alpn", ""),
                "server": host_port[0],
                "port": port,
                "type": "vless",
                "uuid": parts[0].split("@")[0],
                "alterId": 32,
                "cipher": "auto",
                "network": params_dict.get("type", ""),
                "tls": params_dict.get("security", "") == "tls",
                "h2-opts": {
                    "host": [params_dict.get("host", "")],
                    "path": params_dict.get("path", "")
                }
            }

            parsed_data.append(item)
            node_name_data_list.append(params_dict.get("alpn", ""))
            continue
        
        
        # 处理vless + grpc 的情况
        elif line.startswith("vless://") and ("grpc" in line):
            info = line[8:]
            parts = info.split("?", 1)
            
            params_dict = {}
            if len(parts) > 1:
                params = parts[1].split("&")
                for param in params:
                    key, value = param.split("=")
                    params_dict[key] = value
                    
                    
            host_port = parts[0].split("@")[1].split(":")
            if len(host_port) > 1:
                port = int(host_port[-1])
            else:
                port = None
                
            item = {
                "name": params_dict.get("alpn", ""),
                "server": host_port[0],
                "port": port,
                "type": "vless",
                "uuid": parts[0].split("@")[0],
                "alterId": 32,
                "cipher": "auto",
                "network": params_dict.get("type", ""),
                "tls": params_dict.get("security", "") == "tls",
                "servername": params_dict.get("sni", ""),
                "grpc-opts": {
                    "grpc-service-name": params_dict.get("serviceName", "")
                }
            }
            
            parsed_data.append(item)
            node_name_data_list.append(params_dict.get("alpn", ""))
            continue
        
        else:
            raise Exception("订阅中出现了未知的类型")
        

    
    if fun_param == "proxy":
        return parsed_data
    elif fun_param == "proxy-groups":
        return node_name_data_list
    else:
        raise Exception("函数输入中出现了未知的类型")
            
            
# 所有vless节点
parsed_data_list = custom_okgg_yaml_parser_2023_v1(decoded_data,"proxy")
# 所有节点名字
node_name_data_list = custom_okgg_yaml_parser_2023_v1(decoded_data,"proxy-groups")

yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=2)  # 设置缩进
yaml.preserve_quotes = True  # 保留引号


def get_yaml_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        yaml_data = response.text
        # 解析 YAML 数据
        # yaml = ruamel.yaml.YAML()
        parsed_data = yaml.load(yaml_data)
        return parsed_data
    else:
        print("Failed to retrieve YAML file. Status code:", response.status_code)
        return None

# 指定模板 YAML 文件的 URL
yaml_url = "https://gist.githubusercontent.com/cadian2023major/92f23933fb910b91cc81be44eed5d4fe/raw/a722421099d4e713549fad6e5b810154e5ddddc6/OriginRule.yaml"

# 调用函数获取 YAML 数据
data = get_yaml_from_url(yaml_url)


# 从带有注释的 YAML 文件加载数据
#data = yaml.load(open(r'E:\OneDrive\Config\Clash-Verge\OriginRule.yaml', 'r',encoding='utf-8'))

print(type(data))

# 将加载的数据转换为 CommentedMap 类型
if isinstance(data, CommentedMap):
    commented_data = data
else:
    commented_data = CommentedMap(data)
    
# 添加节点数据
commented_data['proxies'] = parsed_data_list
proxy_name_list = parsed_data_list
# 在proxy-groups中添加节点名
commented_data['proxy-groups'][0]
proxy_groups_selection = data['proxy-groups'][0]
proxy_groups_selection['proxies'] = node_name_data_list

# 输出带有注释的 YAML 数据
yaml.dump(commented_data, open('example_modified.yaml', 'w',encoding='utf-8'))
