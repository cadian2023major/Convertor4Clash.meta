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

        
# 自定义解析器  提取 chatgpt相关节点
def custom_okgg_yaml_parser_2023_v2(data, fun_param):
    
    parsed_data = []
    node_name_data_list = []
    
    
    # 添加vless自建中转节点
    node_build = {
                "name": "NodeBuild",
                "type": "vless",
                "server": "",
                "port": ,
                "uuid": ""
            }
    parsed_data.append(node_build)
    node_name_data_list.append("NodeBuild")
    
    lines = data.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("ss://"):
            continue
        
        # 处理vless + h2 的情况
        elif line.startswith("vless://") and ("h2" in line) and ("chatgpt" in line.lower()):
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
        elif line.startswith("vless://") and ("grpc" in line) and  ("chatgpt" in line.lower()):
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
            
        elif line.startswith("vless://"):
            # print("普通vless节点，无法访问chatgpt，直接抛弃")
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
parsed_data_list = custom_okgg_yaml_parser_2023_v2(decoded_data,"proxy")
# 所有节点名字
node_name_data_list = custom_okgg_yaml_parser_2023_v2(decoded_data,"proxy-groups")

yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=2)  # 设置缩进
yaml.preserve_quotes = True  # 保留引号


def get_yaml_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        yamlexample_data = response.text
        # 解析 YAML 数据
        # yaml = ruamel.yaml.YAML()
        parsed_data = yaml.load(yamlexample_data)
        return parsed_data
    else:
        print("Failed to retrieve YAML file. Status code:", response.status_code)
        return None

# 指定 YAML 文件的 URL
yamlexample_url = "https://gist.githubusercontent.com/cadian2023major/92f23933fb910b91cc81be44eed5d4fe/raw/a722421099d4e713549fad6e5b810154e5ddddc6/OriginRule.yaml"

# 调用函数获取 YAML 数据
data = get_yaml_from_url(yamlexample_url)


# 从带有注释的 YAML 文件加载数据
#data = yaml.load(open(r'E:\OneDrive\Config\Clash-Verge\OriginRule.yaml', 'r',encoding='utf-8'))

# 将加载的数据转换为 CommentedMap 类型
if isinstance(data, CommentedMap):
    commented_data = data
else:
    commented_data = CommentedMap(data)
    
# 添加节点数据
commented_data['proxies'] = parsed_data_list

# 初始化空值, 顺手添加自己的节点
commented_data['proxy-groups'][0]['proxies'] = node_name_data_list[0:1]
# 添加relay
for node in node_name_data_list[1:]:
    relay_item = {
        "name":"chain" + node,
        "type":"relay",
        "proxies": 
            [node_name_data_list[0],
            node]
    }
        
    commented_data['proxy-groups'].append(relay_item)
    commented_data['proxy-groups'][0]['proxies'].append("chain" + node)

# 输出带有注释的 YAML 数据
yaml.dump(commented_data, open('ChatgptChainAuto.yaml', 'w',encoding='utf-8'))
print("成功生成配置文件，默认位置 windows在用户目录下")
