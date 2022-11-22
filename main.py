import sys
try:
    from command_runner.elevate import elevate
except Exception as e:
    sys.exit()

def main():
    try:
        import core.splash as splashScreen
        splashScreen.splashScreen.mainloop()
    except (ImportError, ModuleNotFoundError) as e:
        sys.exit("Import error")

if __name__=="__main__":
    # main()
    elevate(main)