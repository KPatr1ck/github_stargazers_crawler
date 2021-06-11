# GitHub Stargazers Crawler

本项目采用了GitHub官方的api，提供从指定repo爬取关注者(stargazers)的id和邮箱信息的功能。  
由于匿名调用官方的api的访问限制条件苛刻(匿名用户每小时60次，参考[Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting))，为了保持爬取脚本的顺利运行，本项目要求用户自行[申请token](https://github.com/settings/tokens)，获取了token之后通过简单的配置即可运行。


## 环境准备

- 系统环境：Linux, MacOS, Windows
-  python3.7+


## 安装

1. Clone本项目代码

   ```shell
   git clone https://github.com/KPatr1ck/github_stargazers_crawler
   ```

2. 安装依赖

   ```shell
   pip install -r requirements.txt
   ```


## 运行脚本

1. 登陆GitHub，[获取token](https://github.com/settings/tokens)。
2. 用`*.json`格式文件配置token和需要爬取的repos地址。
   ```json
   {
       "token": "Your token",
       "repos": {
           "Repo1": "https://github.com/url_of_repo1",
           "Repo2": "https://github.com/url_of_repo2"
       }
   }
   ```
   注意：
   - "token"和"repos"都是必填的键值对
   - "repos"中最少要有一个元素
   - "repos"里嵌套的键值对中，repo的名字可以任取(示例的"Repo1"和"Repo2")

3. 脚本运行和参数
   ```shell
   python main.py --repos ./repos.json --output_dir ./output --num_workers 64 --api_limit_threshold 200
   ```
   参数：
    - repos: 必填，值为上述配置文件的路径。
    - output_dir: 可选，爬取结果文件的存储路径，默认为`./output`。
    - num_workers: 可选，爬虫的线程数，默认为100。
    - api_limit_threshold: 可选，当前token的访问限制小于此值时，工作线程进入睡眠，1小时后再继续爬取数据，默认为200。


## 运行结果  

运行后将在输出目录中生成关注者名单`*.txt`和邮箱信息`*.csv`文件。  

[**注意**]即使使用token，每小时也存在访问限制。当访问限制低于阈值时，工作线程会睡眠1小时后再继续工作。因此，如果爬取的数量过大时，需要等待较长时间。


## TODO

- 支持多个token切换。
