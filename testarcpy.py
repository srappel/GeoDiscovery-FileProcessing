def tryarcpy() -> str:
    try:
        import arcpy
        return "pass"
    except:
        return "fail"

if __name__ == "__main__":
    tryarcpy()
