# unity\_re
tools for idiots. name pending

## rationale
i am decompiling a unity project; i'm developing this tool to hack around the project files and to help identify object relationships, so i can automate some porting processes.

porting old decompiled unity projects is hard. since i started i've been continually learning that theres more and more dumb shit that i need to implement/fix/decompile/etc. i've never used unity before to this degree, so it's a fun time, but its quite a lot.

a lot of the functionality is use-specific and half baked. it may not be for you; i don't know what i'm really doing. but i do hope it could be useful. if you fork this and fix something, please submit a pr or atleast link your fork in an issue so this can get improved...

## running
requires `unityparser` to parse unity yaml; https://pypi.org/project/unityparser/

if you just want to get it going you can execute everything from `./src/main.py` - install the requirements via `pip install -r requirements.txt` and get truckin'

if you have a venv you can install the script; `pip install -e .`

currently, the python argparse module does not print the helptext for subparsers so flags for each available command isn't clear - see main.py to see each command and what it takes and how it takes it.

## tools
id like a more experienced unity expert to weigh in on my notes here...

### find shaders
searches through your project to find as many references to shaders as it can, and prints where it finds them. this includes legacy shaders. useful for deciphering what a shader was used for (because deciphering what a shader did via filename `Shader.shader` isn't helpful...)

this currently searches all materials and unity scenes. expansion pending as needed. there are some missing references in my project that i haven't dug through yet.

### convert legacy particle systems
(VERY HALF BAKED LOL, POSSIBLY INACCURATE???) c# > python conversion of this great unity 2018 script from a unity software engineer that converts legacy particle systems to their modern equivalents - original is here: https://gist.github.com/karljj1/58f16e936d13a94ae6a2f741fd271d91

spits out json that should be equivalent to the settings converted in the tool. the output targets the ParticleSystem structure used in unity 6.

the reason for its port is because this tool only runs on versions of unity below 2018.3 which is frustrating because thats not what im targetting. :( and writing a python script was easier than porting this c# script to a newer version of unity.

### find uid discontinuities
finds discontinuities in unity GameObject IDs.

in decompiled projects (or all?? dont have much to sample...) the ids of GameObjects in a unity scene are a mostly consecutive discrete sequence of integers. loading this scene in newer versions of unity and saving it can result in the editor silently deleting deprecated objects from your project (for me, this was particle systems and legacy gui objects; EllipsoidParticleEmitter, GUIText, GUILayer, etc). this can be frustrating if you're porting a project to a newer version, so this tool can identify if some things get removed.
