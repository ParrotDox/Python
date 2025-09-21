__LANGS__ = ["en","ru","jp"]
lang_name = (str(input("Input language name: "))).lower()
lang_symbols = int(input("Input how many symbols in an alphabet: "))
lang_info_string = lang_name + f"-x{lang_symbols}"


if __LANGS__[0] in lang_info_string:
    print(f"English-x{lang_symbols}")
elif __LANGS__[1] in lang_info_string:
    print(f"Russian-x{lang_symbols}")
else:
    print(f"Unknown-x{lang_symbols}")
    