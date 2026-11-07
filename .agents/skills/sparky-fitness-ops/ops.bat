@echo off
set SSH_KEY="C:\Users\super\.ssh\ssh-key-2026-09-13.key"
set SERVER=opc@158.101.162.138
set CONTAINER=sparkyfitness-server-tdgslqbqhgxxznsokm7gfpun
set CLI="C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py"

if "%1"=="logs" (
    ssh -i %SSH_KEY% %SERVER% "sudo docker logs %CONTAINER% --since 20m 2>&1 | grep -v '/api/health'"
) else if "%1"=="restart" (
    ssh -i %SSH_KEY% %SERVER% "sudo docker restart %CONTAINER%"
) else if "%1"=="summary" (
    python %CLI% summary
) else if "%1"=="audit" (
    python %CLI% audit --fix
) else (
    echo Usage: ops [logs^|restart^|summary^|audit]
)
