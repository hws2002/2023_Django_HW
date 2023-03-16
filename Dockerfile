# TODO Start: [Student] Complete Dockerfile
FROM python:3.9

# 设定 DEPLOY 环境变量为 1
ENV DEPLOY=1

# 工作目录为 /opt/tmp；
WORKDIR /opt/tmp

# 将源代码复制到工作目录
COPY . .
# 安装 requirements.txt 声明的依赖并通过换源到 TUNA 加速下载；
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

#对外暴露 80 端口；
EXPOSE 80

# 容器运行时执行 start.sh 脚本。
CMD ["sh","start.sh"]
# TODO End: [Student] Complete Dockerfile