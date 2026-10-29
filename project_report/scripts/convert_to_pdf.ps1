$docPath = (Resolve-Path "output\Final_Project_Report.docx").Path
$pdfPath = [System.IO.Path]::Combine((Split-Path $docPath), "Final_Project_Report.pdf")

Write-Host "Opening Word Application..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    Write-Host "Opening document: $docPath"
    $doc = $word.Documents.Open($docPath)
    
    # Update all fields including TOC and page numbers
    Write-Host "Updating fields..."
    $doc.Fields.Update()
    
    Write-Host "Exporting to PDF: $pdfPath"
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]$wdFormatPDF)
    
    $doc.Close([ref]$false)
    Write-Host "SUCCESS: PDF generated successfully!"
}
catch {
    Write-Error "ERROR during PDF generation: $_"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
