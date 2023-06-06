del cy_moleculab.html
del cy_moleculab.c
rd /s /q build

del cy_moleculab_310_64.pyd
"C:\Users\JF\AppData\Local\Programs\Python\Python310\python.exe" setup.py build_ext --inplace
del cy_moleculab.html
del cy_moleculab.c
rd /s /q build
ren cy_moleculab_310_64.cp310-win_amd64.pyd cy_moleculab_310_64.pyd

move cy_moleculab_310_64.pyd ..\moleculab\cy_moleculab_310_64.pyd

pause