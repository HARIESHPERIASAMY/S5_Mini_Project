$docxPath = "C:\Users\HARIESH\Downloads\S5 Mini Project\output\SentinelMesh_Final_Report.docx"
$pdfPath  = "C:\Users\HARIESH\Downloads\S5 Mini Project\output\SentinelMesh_Final_Report.pdf"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $doc = $word.Documents.Open($docxPath)
    $doc.ExportAsFixedFormat($pdfPath, 17)   # 17 = wdExportFormatPDF
    $doc.Close($false)
    $word.Quit()
    Write-Host "SUCCESS: PDF saved to $pdfPath"
} catch {
    Write-Host "ERROR: $_"
    try { $word.Quit() } catch {}
}
