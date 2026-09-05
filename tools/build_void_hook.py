"""Build our new first-party aquifer hook against the installed, pinned SRG runtime.

No downloads or third-party jar edits. Only our own compiled classes are packaged.
Requires JDK 17 and the existing development server libraries. Reproducible zip dates.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile
from gen_deepworks import ROOT

def main():
    project=ROOT/'tools/void_hook'; classes=project/'build/classes'; classes.mkdir(parents=True,exist_ok=True)
    libs=ROOT/'server/libraries'
    runtime=libs/'net/minecraft/server/1.20.1-20230612.114412/server-1.20.1-20230612.114412-srg.jar'
    # Exclude other Minecraft variants so javac sees exactly the SRG classes.
    jars=[runtime]+[p for p in libs.rglob('*.jar') if '/net/minecraft/' not in p.as_posix() and 'forge-1.20.1-47.4.10-server.jar' not in p.name]
    args=['--release','17','-proc:none','-classpath',';'.join(map(str,jars)),'-d',str(classes)]+[str(p) for p in (project/'src').rglob('*.java')]
    argfile=project/'build/javac.args'
    argfile.write_text('\n'.join('"'+a.replace('\\','/')+'"' for a in args))
    subprocess.run(['C:/Program Files/Java/jdk-17/bin/javac.exe','@'+str(argfile)],check=True)
    entries={p.relative_to(classes).as_posix():p.read_bytes() for p in classes.rglob('*.class')}
    entries['META-INF/MANIFEST.MF']=b'Manifest-Version: 1.0\nMixinConfigs: alfheim_void_margin.mixins.json\n\n'
    entries['META-INF/mods.toml']=b'''modLoader="javafml"
loaderVersion="[47,48)"
license="All Rights Reserved"
[[mods]]
modId="alfheim_void_margin"
version="1.0.0"
displayName="Alfheim Void Margin"
description="Regional dry aquifers for the Alfheim Reclaimed Void Margins."
[[dependencies.alfheim_void_margin]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1]"
ordering="NONE"
side="BOTH"
'''
    entries['alfheim_void_margin.mixins.json']=json.dumps({'required':True,'minVersion':'0.8','package':'alfheim.voidmargin.mixin','compatibilityLevel':'JAVA_17','mixins':['NoiseChunkMixin'],'injectors':{'defaultRequire':1}}).encode()
    artifact=ROOT/'mods/alfheim-void-margin-1.0.0.jar'
    with zipfile.ZipFile(artifact,'w',compression=zipfile.ZIP_DEFLATED) as jar:
        for name,data in sorted(entries.items()):
            info=zipfile.ZipInfo(name,(2026,9,5,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; jar.writestr(info,data)
    (project/'build_manifest.json').write_text(json.dumps({'artifact':artifact.name,'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),'sources':{p.relative_to(project).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (project/'src').rglob('*.java')}},indent=2)+'\n')
    print('Built',artifact.name)

if __name__=='__main__': main()
