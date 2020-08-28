import psutil


cpu = psutil.cpu_percent(interval=1)
mem = psutil.virtual_memory()
print(cpu)
print(mem.percent)