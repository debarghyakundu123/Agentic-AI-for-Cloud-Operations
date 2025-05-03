# Temporarily disable SSL verification (if needed)
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    auth = @{
        identity = @{
            methods = @("password")
            password = @{
                user = @{
                    name = "Hackathon_AIML_1"
                    domain = @{ name = "Default" }
                    password = "Hackathon_AIML_1@567"
                }
            }
        }
        scope = @{
            project = @{
                name = "ACE_HACKATHON_AIML"
                domain = @{ name = "Default" }
            }
        }
    }
} | ConvertTo-Json -Depth 10

$keystoneUrl = "https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000/v3/auth/tokens"

try {
    $response = Invoke-WebRequest -Uri $keystoneUrl -Method Post -Headers $headers -Body $body
    $token = $response.Headers['X-Subject-Token']
    Write-Host "✅ Authentication successful! Token: $token"
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $streamReader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $errorResponse = $streamReader.ReadToEnd()
        $streamReader.Close()
        Write-Host "🔍 Detailed Error: $errorResponse"
    }
}
