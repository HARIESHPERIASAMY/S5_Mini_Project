$docxPath = "C:\Users\HARIESH\Downloads\S5 Mini Project\output\Final_Project_Report.docx"
$pdfPath  = "C:\Users\HARIESH\Downloads\S5 Mini Project\output\Final_Project_Report.pdf"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($docxPath)
    $doc.ExportAsFixedFormat($pdfPath, 17)
    $doc.Close($false)
    $word.Quit()
    Write-Host "SUCCESS: PDF -> $pdfPath"
    $size = (Get-Item $pdfPath).Length
    Write-Host "PDF size: $size bytes"
} catch {
    Write-Host "ERROR: $_"
    try { $word.Quit() } catch {}
}
