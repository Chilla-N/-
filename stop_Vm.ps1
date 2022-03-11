#
# Powershell script
#
#

$mongoDbDriverPath = "c:\Program Files (x86)\MongoDB\CSharpDriver 1.7\"
Add-Type -Path "$($mongoDbDriverPath)\MongoDB.Bson.dll"
Add-Type -Path "$($mongoDbDriverPath)\MongoDB.Driver.dll"
$databaseName = "test"
$collectionName = "Vm"
$client = New-Object -TypeName MongoDB.Driver.MongoClient -ArgumentList "mongodb://localhost:27017"
$server = $client.GetServer()
$database = $server.GetDatabase($databaseName)
$collection = $database.GetCollection($collectionName)

$query = @{'trans'=$true}
$col = $collection.FindOne([MongoDB.Driver.QueryDocument]$query)
$service_num = $col["service_num"].value
$VMName = $col["host_id"].value


Stop-VM $VMName -Force

exit


