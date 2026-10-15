"""Regression checks for safe test-server identity, without starting/stopping Java."""
import os
from run_server import JAVA17,MC,FORGE,is_harness_server,ready_for_commands

command=f'java.exe @libraries/net/minecraftforge/forge/{MC}-{FORGE}/win_args.txt nogui'
runtime=os.path.abspath(JAVA17)
assert is_harness_server(command,runtime)
assert is_harness_server(command.replace('/','\\'),runtime.upper())
assert not is_harness_server('java.exe @libraries/net/neoforged/neoforge/21.1.248/win_args.txt nogui',runtime)
assert not is_harness_server(command.replace(FORGE,'47.0.0'),runtime)
assert not is_harness_server(command,'C:/other-java/bin/java.exe')
assert not is_harness_server(None,None)
assert not ready_for_commands('Preparing spawn area: 95%')
assert ready_for_commands('Done (31.072s)! For help, type "help"')
print('SERVER PROCESS GUARD PASS: correct Forge runtime matched; NeoForge, other versions and other Java runtimes excluded')
