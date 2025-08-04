import { Injectable } from '@angular/core';
import { Chart, ChartConfiguration, ChartType } from 'chart.js';

import { zipSync, strToU8 } from 'fflate';

@Injectable({
  providedIn: 'root'
})
export class DownloadService {

    public downloadAsJson(data: any[] | any, filename: string = 'data.json'): void {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        this.download(filename, url)
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
        this.download(filename, url)
      }

    public downloadAsZip(data: any[], zipFilename: string = 'data.zip'): void {
        const zipContents: { [filename: string]: Uint8Array } = {};
      
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
      
        this.addCsvToZip(zipContents, 'main.csv', mainData);
      
        Object.entries(nestedDataMap).forEach(([key, nestedData]) => {
          this.addCsvToZip(zipContents, `${key}.csv`, nestedData);
        });
      
        const zipped = zipSync(zipContents);
        const blob = new Blob([zipped], { type: 'application/zip' });
        const url = window.URL.createObjectURL(blob);
        this.download(zipFilename, url);
      }
        
    private addCsvToZip(zipContents: { [filename: string]: Uint8Array }, filename: string, data: any[]): void {
        if (data.length === 0) return;
    
        const headers = Array.from(new Set(data.flatMap(row => Object.keys(row))));
        const csvRows = data.map(row => headers.map(header => JSON.stringify(row[header] ?? '')).join(','));
        csvRows.unshift(headers.join(','));
    
        const csvString = csvRows.join('\n');
        zipContents[filename] = strToU8(csvString);
    }

    private flattenObject(obj: any, parentKey = ''): any[] {
        let rows: any[] = [{}];
        if (!obj) return rows
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

    private download(filename: string, url: string) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }


    public downloadChart(chart: Chart, filename: string = 'pop-chart.png') {
        const url = chart.toBase64Image('image/png', 1);
        this.download(filename, url)
    }


    public downloadHighResChart(originalChart: Chart, filename: string = 'pop-chart-HD.png') {
        if (!originalChart || !originalChart.canvas) {
          throw new Error('Invalid Chart.js instance');
        }
      
        // Get original canvas and context
        const originalCanvas = originalChart.canvas;
        const originalWidth = originalCanvas.width;
        const originalHeight = originalCanvas.height;
      
        // Create a new canvas with increased resolution
    const scaleFactor = 5;
        const newCanvas = document.createElement('canvas');
        newCanvas.width = originalWidth * scaleFactor;
        newCanvas.height = originalHeight * scaleFactor;
        newCanvas.style.width = `${originalWidth}px`;
        newCanvas.style.height = `${originalHeight}px`;
      
        const ctx = newCanvas.getContext('2d');
        if (!ctx) {
          throw new Error('Failed to get canvas context');
        }
      
        // Extract the type correctly
        const chartConfig = originalChart.config as ChartConfiguration<ChartType>;
        const chartType = chartConfig.type as ChartType; // Ensure correct type assertion

        // Deep clone data and options using JSON serialization
        const clonedData = JSON.parse(JSON.stringify(originalChart.data));
        const clonedOptions = JSON.parse(JSON.stringify(originalChart.options));
        
        // Disable animations to speed up rendering
        clonedOptions.animation = false;

        // Scale font sizes and point sizes
        if (clonedOptions.scales) {
            Object.values(clonedOptions.scales).forEach((scale: any) => {
                if (scale.ticks) {
                    scale.ticks.font = scale.ticks.font || {};
                    scale.ticks.font.size = (scale.ticks.font.size ?? 12) * scaleFactor;
                }
                if (scale.title) {
                    scale.title.font = scale.title.font || {};
                    scale.title.font.size = (scale.title.font.size ?? 12) * scaleFactor;
                }
            });
        }

        if (clonedOptions.plugins?.legend) {
            clonedOptions.plugins.legend.labels = clonedOptions.plugins.legend.labels || {};
            clonedOptions.plugins.legend.labels.font = clonedOptions.plugins.legend.labels.font || {};
            clonedOptions.plugins.legend.labels.font.size = (clonedOptions.plugins.legend.labels.font.size || 12) * scaleFactor;
        }

        if (clonedOptions.plugins?.tooltip) {
            clonedOptions.plugins.tooltip.bodyFont = clonedOptions.plugins.tooltip.bodyFont || {};
            clonedOptions.plugins.tooltip.bodyFont.size = (clonedOptions.plugins.tooltip.bodyFont.size || 12) * scaleFactor;
        }

        // Scale dataset point radius
        if (clonedData.datasets) {
            clonedData.datasets.forEach((dataset: any) => {
                dataset.borderWidth = (dataset.borderWidth ?? 3) * scaleFactor;
                dataset.pointRadius = (dataset.pointRadius ?? 3) * scaleFactor;
                dataset.pointHoverRadius = (dataset.pointHoverRadius ?? 4) * scaleFactor;
            });
        }

        // Clone chart configuration
        const newConfig: ChartConfiguration = {
            type: chartType,
            data: clonedData,
            options: {
                ...clonedOptions,
                responsive: false,
                maintainAspectRatio: false,
            },
        };

        // Create a new chart with increased resolution
        const newChart = new Chart(ctx, newConfig);

      
        // Wait for chart to finish rendering
        const url = newChart.toBase64Image('image/png', 1);
        this.download(filename, url)
      }
      

}