from ConfigParser import ConfigParser,ParsingError

class ConfigException(Exception):
    """Basic exception for the ConfigEngine."""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "ConfigException: " + str(self.message)
    
class ConfigEngine:
    """Handles configuration files for pwlib. Data is represented internally
    as a dictionary of dictionaries."""
    _parser = None

    def __init__(self):
        if (ConfigEngine._parser == None):
            ConfigEngine._parser = ConfigParser()
            
    def load(self, filename):
        """Load configuration from 'filename'."""
        parser = ConfigEngine._parser
        try:
            parser.read(filename)
        except ParsingError,e:
            raise ConfigException(str(e))

        conf = dict()
        for section in parser.sections():
            conf[section] = dict()
            for option in parser.options(section):
                conf[section][option] = parser.get(section, option)

        return conf

    def save(self, filename, cfg):
        """Save the configuration 'cfg' to 'filename'.
        'cfg' is a dictionary of dictionaries."""
        parser = ConfigEngine._parser
        for key in cfg.keys():
            if parser.has_section(key):
                section = parser.section(key)
            else:
                section = parser.add_section(key)
            sectiondict = cfg[key]
            if (type(sectiondict) == dict):
                for optionkey in sectiondict.keys():
                    parser.set(key, optionkey, sectiondict[optionkey])
        try:
            fp = file(filename, "w+")
            parser.write(fp)
            fp.close()
        except IOError, e:
            raise ConfigException(str(e))
        
                
        
