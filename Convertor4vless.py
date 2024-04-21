# 使用说明：
#   1.在V2Ray订阅地址中填入Okgg的订阅地址即可直接运行即可得到配置文件。

# 包含Okgg亚洲节点和韩国自建节点的配置文件
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

        
#   自定义解析器 2024版
#
#   根据节点的不同属性，提取特征进行分类处理
#   --> vless + grpc
#       --> encryption=none
#       --> type=grpc
#       --> headerType=none
#       --> fp=random
#       --> host=自定义内容
#       --> path=自定义内容        TODO 奇怪的是并没有看到这个内容被使用
#       --> flow=空
#       --> security=tls
#       --> sni=自定义内容
#       --> serviceName=自定义内容
#       --> mode=gun
#       --> alpn=空
#       --> 每行最后 #节点名字
#
#
#   --> vless + tcp (xtls-rprx-vision) 
#       --> encryption=none
#       --> type=tcp
#       --> headerType=none
#       --> fp=ios 或者 random
#       --> host=自定义内容
#       --> path=空
#       --> flow=xtls-rprx-vision
#       --> security=tls
#       --> sni=自定义内容
#       --> serviceName=空
#       --> mode=gun
#       --> alpn=空
#       --> 每行最后 #节点名字
def custom_okgg_yaml_parser_2024(data, fun_param):
    
    parsed_data = []
    node_name_data_list = []
    
    # 添加vless自建节点 没有备用的自建节点可以不填
    korea_build = {
        "name": "",
        "type": "vless",
        "server": "",
        "port": "443",
        "uuid": "",
        "network": "tcp",
        "tls": True,
        "udp": True,
        "xudp": True,
        "flow": "xtls-rprx-vision",
        "servername": "",
        "client-fingerprint": "",
        "reality-opts":{
            "public-key": "",
            "short-id": ""
        }
    }
    parsed_data.append(korea_build)
    node_name_data_list.append("KoreaBuild")
    
    lines = data.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("ss://"):
            continue
            
            
        
        # 处理vless + grpc 的情况
        elif line.startswith("vless://") and ("grpc" in line):
            # 去掉报文头部
            info = line[8:]
            # ? 后面是有用信息
            parts = info.split("?", 1)
            # 早期有过一段混乱时期 ， 格式不工整 ， 在这里直接进行输出, 方便debug
            if "alpn" not in parts[1]:
                print("信息不工整，请进行检查")
                print(parts[1])
                
            params_dict = {}
            # 有效信息部分是用 & 符号进行链接的，在这里拆分，重新打包到字典
            if len(parts) > 1:
                params = parts[1].split("&")
                for param in params:
                    key, value = param.split("=")
                    params_dict[key] = value
                    
            # 获取服务器端口，服务器端口在 ? 之前的内容中，先用@拆分，然后找到:之前的服务器域名和:之后的端口
            host_port = parts[0].split("@")[1].split(":")
            if len(host_port) > 1:
                port = int(host_port[-1])
            else:
                port = None
                
                
            # 对节点内容进行拼接
            # Example:
            # -   name: "vless-reality-grpc"
            #     type: vless
            #     server: server
            #     port: 443
            #     uuid: uuid
            #     network: grpc
            #     tls: true
            #     udp: true
            #     flow:
            #     # skip-cert-verify: true
            #     client-fingerprint: chrome
            #     servername: testingcf.jsdelivr.net
            #     grpc-opts:
            #       grpc-service-name: "grpc"
            #     reality-opts:
            #       public-key: CrrQSjAG_YkHLwvM2M-7XkKJilgL5upBKCp0od0tLhE
            #       short-id: 10f897e26c4b9478
            #     完整样例: https://github.com/MetaCubeX/mihomo/blob/Alpha/docs/config.yaml
            
            
            item = {
                "name": params_dict.get("alpn", parts[1].split("#")[-1]),                           # alpn 节点名字
                "type": "vless",                                                                    # 协议种类
                "server": host_port[0],                                                             # server 是域名
                "port": port,                                                                       # 端口
                "uuid": parts[0].split("@")[0],                                                     # uuid
                "network": params_dict.get("type", ""),                                             # 这里直接写 network: grpc也一样
                "tls": params_dict.get("security", "") == "tls",                                    # 这里直接写 tls: true也一样
                "udp": True,                                                                        # udp 不解释
                "flow": params_dict.get("flow", ""),                                                # 流控类型
                "client-fingerprint": params_dict.get("fp", ""),                                    # 指纹类型
                "servername": params_dict.get("sni", ""),                                           # 伪装域名
                "grpc-opts": {
                    "grpc-service-name": params_dict.get("serviceName", "").split("#")[0]           # grpc serviceName
                }
            }
            
            # 历史遗留问题
            if "alpn" not in parts[1]:
                item["servername"]=item.get("server")

            parsed_data.append(item)
            node_name_data_list.append(item.get("name", ""))
            continue



        # 处理vless + tcp 的情况
        # xtls-rprx-vision
        # 不畏浮云遮望眼,金睛如炬耀苍穹

        #   - name: "vless-reality-vision"
        #     type: vless
        #     server: server
        #     port: 443
        #     uuid: uuid
        #     network: tcp
        #     tls: true
        #     udp: true
        #     flow: xtls-rprx-vision
        #     servername: www.microsoft.com # REALITY servername
        #     reality-opts:     TODO 这个也没有使用到
        #       public-key: xxx
        #       short-id: xxx # optional
        #     client-fingerprint: chrome # cannot be empty
        #
        #   完整配置文件模板: https://github.com/MetaCubeX/mihomo/blob/Alpha/docs/config.yaml
        elif line.startswith("vless://") and ("tcp" in line) and ("xtls-rprx-vision" in line):
            # 去掉报文头部
            info = line[8:]
            # ? 后面是有用信息
            parts = info.split("?", 1)
            # 早期有过一段混乱时期 ， 格式不工整 ， 在这里直接进行输出, 方便debug
            if "alpn" not in parts[1]:
                print("信息不工整，请进行检查")
                print(parts[1])
                
            params_dict = {}
            # 有效信息部分是用 & 符号进行链接的，在这里拆分，重新打包到字典
            if len(parts) > 1:
                params = parts[1].split("&")
                for param in params:
                    key, value = param.split("=")
                    params_dict[key] = value
                    
            # 获取服务器端口，服务器端口在 ? 之前的内容中，先用@拆分，然后找到:之前的服务器域名和:之后的端口
            host_port = parts[0].split("@")[1].split(":")
            if len(host_port) > 1:
                port = int(host_port[-1])
            else:
                port = None

            item = {
                "name": params_dict.get("alpn", parts[1].split("#")[-1]),                           # alpn 节点名字
                "type": "vless",                                                                    # 协议种类
                "server": host_port[0],                                                             # server 是域名
                "port": port,                                                                       # 端口 其实这种情况也就是443
                "uuid": parts[0].split("@")[0],                                                     # uuid
                "network": params_dict.get("type", ""),                                             # 这里直接写 network: grpc也一样
                "tls": params_dict.get("security", "") == "tls",                                    # 这里直接写 tls: true也一样
                "udp": True,                                                                        # udp 不解释
                "flow": params_dict.get("flow", ""),                                                # 流控类型
                "servername": params_dict.get("sni", ""),                                           # 伪装域名
                "client-fingerprint": params_dict.get("fp", ""),                                    # 指纹类型
                "reality-opts": {
                    "grpc-service-name": params_dict.get("serviceName", "").split("#")[0]           # grpc serviceName
                }
            }

            parsed_data.append(item)
            node_name_data_list.append(item.get("name", ""))
            continue
        

        # 处理vless + h2 的情况
        # 快过时的处理方法
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
                "name": params_dict.get("alpn", ),
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
            node_name_data_list.append(params_dict.get("name", ""))
            continue
        

            
        elif line.strip() == "":
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
parsed_data_list = custom_okgg_yaml_parser_2024(decoded_data,"proxy")
# 所有节点名字
node_name_data_list = custom_okgg_yaml_parser_2024(decoded_data,"proxy-groups")

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
yamlexample_url = "https://gist.githubusercontent.com/cadian2023major/92f23933fb910b91cc81be44eed5d4fe/raw/96419821f3b17da079037990ca2e0c56b32aa0bc/OriginRule.yaml"

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


# 在proxy-groups中添加节点名
proxy_groups_selection = commented_data['proxy-groups'][0]
proxy_groups_selection['proxies'] = node_name_data_list

# 初始化空值, 顺手添加自己的节点
#commented_data['proxy-groups'][0]['proxies'] = node_name_data_list[0:1]

# 输出带有注释的 YAML 数据, 这里选择直接输出到clash verge的配置文件中，省略了手动修改的一步
yaml.dump(commented_data, open('C:/Users/flyho/AppData/Roaming/io.github.clash-verge-rev.clash-verge-rev/profiles/XXX.yaml', 'w',encoding='utf-8'))
print("成功生成配置文件")
