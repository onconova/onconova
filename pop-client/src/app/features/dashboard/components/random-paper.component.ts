import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { catchError, map, of} from 'rxjs';
import { InlineSVGModule } from 'ng-inline-svg-2';
import { Skeleton } from 'primeng/skeleton';
import { Button } from 'primeng/button';
import { rxResource } from '@angular/core/rxjs-interop';


@Component({
    selector: 'pop-random-paper',
    imports: [
      CommonModule, 
      Button, 
      Skeleton, 
      InlineSVGModule],
    template: `
    <div class="paper-details">
        <div [inlineSVG]="illustration" class="paper-illustration"></div>
        <div class="my-auto ml-3 flex flex-column w-full">
            @if (paperResource.isLoading()) {
              <p-skeleton width="100%" height="7rem" />
            } @else {
              @if (paperResource.value(); as paper) {
                <div>
                    <div class="font-semibold mb-1"><small>Research paper</small></div>
                    <div class="mb-1"><i>{{ paper.title[0] }}</i></div>
                    
                      <p class="mb-3"> 
                        @if (paper.author; as authors) {
                          {{ authors[0].family }} et al., 
                        }{{ paper['container-title'] }}, {{ paper['journal-issue']?.issue || '?' }}, {{ paper['published-print']?.['date-parts'][0][0] || '' }}
                      </p>
                    <a [href]="paper.URL" target="_blank"><p-button icon="pi pi-arrow-right" label="Access the publication"/></a>
                </div>
              }
            } 
        </div>
    </div>
  `
})
export class RandomPaperComponent {

  readonly #http = inject(HttpClient);

  readonly illustration: string = 'assets/images/landing/papers.svg';

  public paperResource = rxResource({
    request: () => this.constructAPIcall(),  
    loader:  ({request}) => this.#http.get(request).pipe(
      catchError(() => this.#http.get(this.constructAPIcall()))
      ).pipe(
      map((response: any) => {
      const papers = response.message.items;
      if (papers && papers.length > 0) {
          // Determine a paper based on today's date
          const index = this.getDateBasedIndex(papers.length);
          return papers[index];
      }
      }),
    )
  });

  // Helper function to generate a deterministic hash based on the current date
  private getDateBasedIndex(length: number): number {
    const today = new Date().toISOString().split('T')[0]; // Get today's date (e.g., "2025-01-23")
    let hash = 0;
    for (let i = 0; i < today.length; i++) {
      hash = (hash << 5) - hash + today.charCodeAt(i);
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash) % length; // Ensure a valid index within bounds
  }

  // Generate a dynamic random date filter
  private generateDynamicDateFilter(): string {
    const today = new Date();
    const randomDaysOffset = this.getDateBasedIndex(5*365); // Random offset up to 1 year
    const randomDate = new Date(today);
    randomDate.setDate(today.getDate() - randomDaysOffset); // Subtract offset days
    return randomDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
  }

  constructAPIcall(dateFilter: boolean = true) {
    const baseUrl = 'https://api.crossref.org/works';
    const query = 'cancer';
    const filters = `type:journal-article` + (dateFilter ? `,from-pub-date:${this.generateDynamicDateFilter()}` : '');
    const rows = 1; // Maximum number of papers to retrieve

    // Construct API URL
    return `${baseUrl}?query=${encodeURIComponent(query)}&filter=${filters}&rows=${rows}&sort=published&order=asc`;
  }
}