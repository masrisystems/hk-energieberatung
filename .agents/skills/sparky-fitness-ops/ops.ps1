param(
    [Parameter(Position=0)]
    [ValidateSet("logs", "restart", "summary", "audit")]
    [string]$Command = "summary"
)

$SshKey = "C:\Users\super\.ssh\ssh-key-2026-09-13.key"
$Server = "opc@158.101.162.138"
$Container = "sparkyfitness-server-tdgslqbqhgxxznsokm7gfpun"
$Cli = "C:\Users\super\.agents\skills\nutritional-specialist\scripts\sparky_fitness.py"

switch ($Command) {
    "logs" {
        ssh -i $SshKey $Server "sudo docker logs $Container --since 20m 2>&1 | grep -v '/api/health'"
    }
    "restart" {
        ssh -i $SshKey $Server "sudo docker restart $Container"
    }
    "summary" {
        python $Cli summary
    }
    "audit" {
        python $Cli audit --fix
    }
}
