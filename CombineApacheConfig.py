#!/usr/bin/python2.7
# CombineApacheConfig.py 

__author__ = 'ben'
import sys, os, os.path, logging, fnmatch, re


def Help():
    print("Usage: python CombineApacheConfig.py inputfile[default:/etc/apache2/apache2.conf] outputfile[default:/tmp/apache2.combined.conf")


def InputParameter():
    if len(sys.argv) <> 3:
        Help()
        return "/etc/apache2/apache2.conf", "/tmp/apache2.combined.conf"
    return sys.argv[1], sys.argv[2]


def ProcessMultipleFiles(InputFiles):
    if InputFiles.endswith('/'):              #Updated as Pierrick's comment
        InputFiles = InputFiles + "*"
    Content = ''
    LocalFolder = os.path.dirname(InputFiles)
    basenamePattern = os.path.basename(InputFiles)
    for root, dirs, files in os.walk(LocalFolder):
        for filename in fnmatch.filter(files, basenamePattern):
            Content += ProcessInput(os.path.join(root, filename))
    return Content


def RemoveExcessiveLinebreak(s):
    Length = len(s)
    s = s.replace(os.linesep + os.linesep + os.linesep, os.linesep + os.linesep)
    NewLength = len(s)
    if NewLength < Length:
        s = RemoveExcessiveLinebreak(s)
    return s


def ProcessInput(InputFile):
    global ServerRoot

    Content = ''
    if logging.root.isEnabledFor(logging.DEBUG):
        Content = '# Start of ' + InputFile + os.linesep
    with open(InputFile, 'r') as infile:
        for line in infile:
            stripline = line.strip(' \t')
            if stripline.startswith('#'):
                continue
            searchroot = re.search(r'ServerRoot\s+(\S+)', stripline, re.I)      #search for ServerRoot
            if searchroot:
                ServerRoot = searchroot.group(1).strip('"')
                logging.info("ServerRoot: " + ServerRoot)
            if stripline.lower().startswith('include'):
                match = stripline.split()
                if len(match) == 2:
                    IncludeFiles = match[1]
                    IncludeFiles = IncludeFiles.strip('"') #Inserted according to V's comment.
                    if not IncludeFiles.startswith('/'):
                        IncludeFiles = os.path.join(ServerRoot, IncludeFiles)

                    Content += ProcessMultipleFiles(IncludeFiles) + os.linesep
                else:
                    Content += line     # if it is not pattern of 'include(optional) path', then continue.
            else:
                Content += line
    Content = RemoveExcessiveLinebreak(Content)
    if logging.root.isEnabledFor(logging.DEBUG):
        Content += '# End of ' + InputFile + os.linesep + os.linesep
    return Content


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s][%(levelname)s]:%(message)s')
    InputFile, OutputFile = InputParameter()
    try:
        ServerRoot = os.path.dirname(InputFile)
        Content = ProcessInput(InputFile)
    except Exception as e:
        logging.error("Failed to process " + InputFile,  exc_info=True)
        exit(1)

    try:
        with open(OutputFile, 'w') as outfile:
            outfile.write(Content)
    except Exception as e:
        logging.error("Failed to write to " + outfile,  exc_info=True)
        exit(1)

    logging.info("Done writing " + OutputFile)


