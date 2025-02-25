import { Injectable } from '@angular/core';

import JSZip from 'jszip';

@Injectable({
  providedIn: 'root'
})
export class DownloadService {

    public downloadAsJson(data: any[], filename: string = 'data.json'): void {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }

    public downloadAsFlatCsv(data: any[], filename: string = 'data.csv'): void {
        if (data.length === 0) return;
                
        const flattenedData = data.flatMap(item => this.flattenObject(item));
        const headers = Array.from(new Set(flattenedData.flatMap(row => Object.keys(row))));
        const csvRows = flattenedData.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','));
        csvRows.unshift(headers.join(',')); // Add header row
        
        const csvString = csvRows.join('\n');
        const blob = new Blob([csvString], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }

    public downloadAsZip(data: any[], zipFilename: string = 'data.zip'): void {
        const zip = new JSZip();
        
        const mainData: any[] = [];
        const nestedDataMap: { [key: string]: any[] } = {};
        
        data.forEach(item => {
        const flatObj: any = {};
        const pseudoIdentifier = item.pseudoidentifier || '';
        
        Object.entries(item).forEach(([key, value]) => {
            if (Array.isArray(value)) {
            if (!nestedDataMap[key]) nestedDataMap[key] = [];
            value.forEach(subItem => {
                const nestedRow = { pseudoidentifier: pseudoIdentifier, ...this.flattenObject(subItem)[0] };
                nestedDataMap[key].push(nestedRow);
            });
            } else if (typeof value === 'object' && value !== null) {
            if (!nestedDataMap[key]) nestedDataMap[key] = [];
            const nestedRow = { pseudoidentifier: pseudoIdentifier, ...this.flattenObject(value)[0] };
            nestedDataMap[key].push(nestedRow);
            } else {
            flatObj[key] = value;
            }
        });
        mainData.push(flatObj);
        });
        
        this.addCsvToZip(zip, 'main.csv', mainData);
        
        Object.entries(nestedDataMap).forEach(([key, nestedData]) => {
        this.addCsvToZip(zip, `${key}.csv`, nestedData);
        });
        
        zip.generateAsync({ type: 'blob' }).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = zipFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        });
    }
        
    private addCsvToZip(zip: JSZip, filename: string, data: any[]): void {
        if (data.length === 0) return;
        const headers = Array.from(new Set(data.flatMap(row => Object.keys(row))));
        const csvRows = data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','));
        csvRows.unshift(headers.join(','));
        zip.file(filename, csvRows.join('\n'));
    }

    private flattenObject(obj: any, parentKey = ''): any[] {
        let rows: any[] = [{}];
        
        Object.entries(obj).forEach(([key, value]) => {
            const newKey = parentKey ? `${parentKey}.${key}` : key;
            
            if (Array.isArray(value)) {
            const expandedRows = value.flatMap(item => this.flattenObject(item, newKey));
            rows = expandedRows.map(expandedRow => ({ ...rows[0], ...expandedRow }));
            } else if (typeof value === 'object' && value !== null) {
            rows = rows.map(row => ({ ...row, ...this.flattenObject(value, newKey)[0] }));
            } else {
            rows.forEach(row => row[newKey] = value);
            }
        });
        
        return rows;
    }

}