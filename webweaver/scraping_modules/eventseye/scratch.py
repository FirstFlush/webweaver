import toml



def get_toml():
    config_path = "./eventseye.toml"
    config = toml.load(config_path)
    # print(type(config))
    print(config)
    model_names = config['models']['names']

    # print(model_names)


get_toml()