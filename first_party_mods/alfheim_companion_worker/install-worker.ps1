param(
    [string]$InstanceRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

$ErrorActionPreference = 'Stop'
$workerProject = (Resolve-Path $PSScriptRoot).Path
$companionProject = (Resolve-Path (Join-Path $PSScriptRoot '..\alfheim_companion')).Path
$gradleWrapper = Join-Path $companionProject 'gradle\wrapper\gradle-wrapper.jar'
$java17 = 'C:\Program Files\Java\jdk-17\bin\java.exe'
$installRoot = Join-Path $InstanceRoot 'alfheim_companion\inference'
$workerTarget = Join-Path $installRoot 'worker'
$runtimeTarget = Join-Path $installRoot 'runtime'
$modelsTarget = Join-Path $installRoot 'models'

if (-not (Test-Path -LiteralPath $java17 -PathType Leaf)) {
    throw "JDK 17 is required to run the project build: $java17"
}

& $java17 -classpath $gradleWrapper org.gradle.wrapper.GradleWrapperMain -p $workerProject installDist
if ($LASTEXITCODE -ne 0) { throw 'Worker build failed.' }

$toolchains = Join-Path $env:USERPROFILE '.gradle\jdks'
$java21 = Get-ChildItem -LiteralPath $toolchains -Directory -ErrorAction Stop |
    Where-Object Name -like '*21*windows*' |
    ForEach-Object { Get-ChildItem -LiteralPath $_.FullName -Directory | Select-Object -First 1 } |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'bin\java.exe') } |
    Select-Object -First 1
if ($null -eq $java21) { throw 'Gradle did not provision the required Java 21 toolchain.' }

New-Item -ItemType Directory -Path $installRoot -Force | Out-Null
New-Item -ItemType Directory -Path $workerTarget -Force | Out-Null
New-Item -ItemType Directory -Path $runtimeTarget -Force | Out-Null
Get-ChildItem -LiteralPath (Join-Path $workerProject 'build\install\alfheim-companion-worker') |
    Copy-Item -Destination $workerTarget -Recurse -Force
Get-ChildItem -LiteralPath $java21.FullName |
    Copy-Item -Destination $runtimeTarget -Recurse -Force

& (Join-Path $runtimeTarget 'bin\java.exe') --enable-preview --add-modules=jdk.incubator.vector `
    -Xms128m -Xmx512m -cp (Join-Path $workerTarget 'lib\*') `
    com.continuityworks.alfheimcompanion.worker.WorkerMain --download --models-root $modelsTarget
if ($LASTEXITCODE -ne 0) { throw 'Model download failed.' }

Write-Host "Installed Alfheim Companion inference under $installRoot"
