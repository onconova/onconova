import { TestBed } from '@angular/core/testing';
import { DownloadService } from './download.service';


function spyOnExpectedDownload(done: any, expectedData: any, mimeType: string) {
    spyOn(window.URL, 'createObjectURL').and.callFake((blob: Blob) => {
        expect(blob).toBeInstanceOf(Blob);
        expect(blob.type).toBe(mimeType);

        const reader = new FileReader();
        reader.onload = () => {
            if(expectedData) {
                expect(reader.result).toBe(expectedData);
            }
        };
        reader.readAsText(blob);
        return 'blob-url-mock';
    });
}

function mockAnchorElement(done: any, filename: string) {
    // Mock anchor element to prevent actual download
    const mockAnchor = document.createElement('a');
    spyOn(document, 'createElement').and.returnValue(mockAnchor);
    spyOn(mockAnchor, 'click').and.callFake(() => {
      // Ensure it attempts to set correct download attributes
      expect(mockAnchor.href).toContain('blob-url-mock');
      expect(mockAnchor.download).toBe(filename);
      done();
    });
}

describe('DownloadService', () => {
  let service: DownloadService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [DownloadService]
    });
    service = TestBed.inject(DownloadService);
  });

  it('should be able to download an empty JSON file', (done) => {
    const data: any[] = [];
    const filename = 'empty.json';
    const expectedData = JSON.stringify(data, null, 2);
    spyOnExpectedDownload(done, expectedData, 'application/json')  
    mockAnchorElement(done, filename)
    service.downloadAsJson(data, filename);
  });

  it('should be able to download a JSON file', (done) => {
    const data = [{ foo: 'bar' }];
    const filename = 'data.json';
    const expectedData = JSON.stringify(data, null, 2);
    spyOnExpectedDownload(done, expectedData, 'application/json')
    mockAnchorElement(done, filename)
    service.downloadAsJson(data, filename);
  });

  it('should be able to download an empty CSV file', (done) => {
    const data: any[] = [{}];
    const filename = 'data.csv';
    const expectedData = '\n';
    spyOnExpectedDownload(done, expectedData, 'text/csv')
    mockAnchorElement(done, filename)
    service.downloadAsFlatCsv(data, filename);
  });
  
  it('should be able to download a CSV file', (done) => {
    const data = [{ foo: 'foo1',  bar: 'bar1'  }];
    const filename = 'data.csv';
    const expectedData = ['foo,bar','"foo1","bar1"'].join('\n');
    spyOnExpectedDownload(done, expectedData, 'text/csv')
    mockAnchorElement(done, filename)
    service.downloadAsFlatCsv(data, filename);
  });
  
  it('should be able to download CSV ZIP file', (done) => {
    const data = [{ foo: 'foo1',  bar: 'bar1'  }];
    const filename = 'data.csv';
    const expectedData = null
    spyOnExpectedDownload(done, expectedData, 'application/zip')
    mockAnchorElement(done, filename)
    service.downloadAsZip(data, filename);
  });

});
