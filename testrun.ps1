#
# Service Catalogue automated test script
#
# To do:
# - run the setup script
# - start the main program
# - execute this script - no arguments needed
#
# Script will output testrun_results.txt with results of all tests
#
# About:
# Uses invoke-webrequest due to need to get access to http return codes.
#

$WebServerAddress = 'http://localhost:8080/'
$ContentType = 'application/json'
$TestResults = @()

# Test 1: Query the test API. Returns 200 OK.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/test') -ContentType $ContentType -Method Get
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 200) -and (-not ([string]::IsNullOrEmpty($response.content))))
{
    $TestResults += "1 Passed"
}
else
{
    $TestResults += "1 Failed"
}


# Test 2: Get all VMs. Returns 200 OK.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm') -ContentType $ContentType -Method Get
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 200) -and (-not ([string]::IsNullOrEmpty($response.content))))
{
    $TestResults += "2 Passed"
}
else
{
    $TestResults += "2 Failed"
}


# Test 3: Create a basic VM. Returns 201 Created.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm') -Body '{"name": "PshellBasic", "ipaddresses": ["10.20.30.0/24"]}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 201) -and ($response.Content.Contains('vm-')))
{
    $TestResults += "3 Passed"
}
else
{
    $TestResults += "3 Failed"
}


# Test 4: Create a VM with multiple IP addresses - returns 201 Created
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm') -Body '{"name": "PshellMultiIP", "ipaddresses": ["10.20.30.0/24", "10.220.30.0/24"]}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 201) -and ($response.Content.Contains('vm-')))
{
    $TestResults += "4 Passed"
}
else
{
    $TestResults += "4 Failed"
}


# Test 5: Fail to create a VM - no IP address specified. Returns 400 Bad Request
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm') -Body '{"name": "MissingIP"}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}
if ($response.StatusCode -eq 'BadRequest')
{
    $TestResults += "5 Passed"
}
else
{
    $TestResults += "5 Failed"
}

# Test 6: Fail to create a VM - incorrect IP address specified. Returns 400 Bad Request
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm') -Body '{"name": "IncorrectIP", "ipaddresses": ["10.20.200.0/27"]}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 'BadRequest')
{
    $TestResults += "6 Passed"
}
else
{
    $TestResults += "6 Failed"
}


# Test 7: Delete a VM. Returns 204 Deleted
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm/vm-2') -ContentType $ContentType -Method Delete
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 204)
{
    $TestResults += "7 Passed"
}
else
{
    $TestResults += "7 Failed"
}


# Test 8: Delete same VM again. Returns 404 Not Found.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/vms/vm/vm-2') -ContentType $ContentType -Method Delete
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 'NotFound')
{
    $TestResults += "8 Passed"
}
else
{
    $TestResults += "8 Failed"
}


# Test 9: Successfully restart a VM. Returns 200 OK with successful message.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/service-operations/restart-vm/vm-1') -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 200) -and ($response.Content.Contains('Successfully restarted')))
{
    $TestResults += "9 Passed"
}
else
{
    $TestResults += "9 Failed"
}


# Test 10: Attempt to restart a VM that is turned off. Returns 200 OK but won't have been able to restart.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/service-operations/restart-vm/vm-4') -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 200) -and ($response.Content.Contains('Unable to restart')))
{
    $TestResults += "10 Passed"
}
else
{
    $TestResults += "10 Failed"
}


# Test 11: Attempt to restart a non-existent VM. Returns 404 Not Found.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/service-operations/restart-vm/vm-146') -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 'NotFound')
{
    $TestResults += "11 Passed"
}
else
{
    $TestResults += "11 Failed"
}

# Test 12: Get all firewall rules. Returns 200 OK.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/network/firewall/rules/rule') -ContentType $ContentType -Method Get
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 200) -and (-not ([string]::IsNullOrEmpty($response.content))))
{
    $TestResults += "12 Passed"
}
else
{
    $TestResults += "12 Failed"
}

# Test 13: Create a firewall rule including an IP address and a subnet. Returns 201 Created.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/network/firewall/rules/rule') -Body '{"name": "RuleIPandSubnet", "from": "10.20.30.16", "to": "10.220.30.0/24", "action": "allow"}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 201) -and ($response.Content.Contains('fw-')))
{
    $TestResults += "13 Passed"
}
else
{
    $TestResults += "13 Failed"
}

# Test 14: Create a firewall rule including a subnet and a vmid. Returns 201 Created
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/network/firewall/rules/rule') -Body '{"name": "RuleSubnetandVmid", "from": "10.70.85.0/25", "to": "vm-23", "action": "allow"}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if (($response.StatusCode -eq 201) -and ($response.Content.Contains('fw-')))
{
    $TestResults += "14 Passed"
}
else
{
    $TestResults += "14 Failed"
}

# Test 15: Attempt to create a firewall rule but fail due to incorrect subnet format. Returns 400 Bad Request.
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/network/firewall/rules/rule') -Body '{"name": "RuleIncorrectSubnet", "from": "10.20.30.0/33", "to": "192.168.5.6", "action": "deny"}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 'BadRequest')
{
    $TestResults += "15 Passed"
}
else
{
    $TestResults += "15 Failed"
}

# Test 16: Attempt to create a firewall rule but fail due to lack of action key. Returns 400 Bad Request
Try
{
    $response = Invoke-WebRequest -Uri ($WebServerAddress + 'api/network/firewall/rules/rule') -Body '{"name": "RuleNoAction", "from": "vm-7", "to": "vm-12"}' -ContentType $ContentType -Method Post
}
Catch
{
    $response = $_.Exception.Response
}

if ($response.StatusCode -eq 'BadRequest')
{
    $TestResults += "16 Passed"
}
else
{
    $TestResults += "16 Failed"
}

# Output the results to a file
$TestResults | Out-File "testrun_results.txt"