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


$databaseName = "admin"
$collectionName = "admin"

$database = $server.GetDatabase($databaseName)
$collection = $database.GetCollection($collectionName)



$query = @{'lable' = $service_num}
$col = $collection.FindOne([MongoDB.Driver.QueryDocument]$query)

$MemoryStartupBytes = $col["MemoryStartupBytes"].value
$NewVHDSizeBytes = $col["NewVHDSizeBytes"].value
$ProcessCore = $col["ProcessCore"].value
$traffic = $col["traffic"].value * 1000000

 
 
 
 $image = "C:\Users\Public\Documents\Hyper-V\iso\Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.iso"
 $VM = @{
     Name = $VMName
     MemoryStartupBytes = $MemoryStartupBytes
     Generation = 2
     NewVHDPath = "D:\$VMName.vhdx"
     NewVHDSizeBytes = $NewVHDSizeBytes #storage
     BootDevice = "VHD"
     Path = "C:\ProgramData\Microsoft\Windows\Hyper-V\"
     SwitchName = "Default Switch"
 }

New-VM @VM
Set-VMNetworkAdapterVlan -VMName $VMName -Access -VlanId 2
Set-VM -VMName $VMName -ProcessorCount $ProcessCore
Set-VMNetworkAdapter -Vmname $VMName  -MaximumBandwidth $traffic
Set-VMProcessor $VMName -Count $ProcessCore
Set-VMDvdDrive -Vmname $VMName -path $image

exit