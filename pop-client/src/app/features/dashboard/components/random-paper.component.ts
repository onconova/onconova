import { Component, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { catchError, map, of} from 'rxjs';
import { InlineSVGModule } from 'ng-inline-svg-2';

import { Skeleton } from 'primeng/skeleton';
import { Button } from 'primeng/button';

@Component({
    selector: 'pop-random-paper',
    imports: [CommonModule, Button, Skeleton, InlineSVGModule],
    template: `
    @let paper = paper$ | async;
    @if (errorMessage) {
        <div class="paper-error-message">
            {{ errorMessage }}
        </div>
    }
    <div class="paper-details">
        <div [inlineSVG]="illustration" class="paper-illustration"></div>
        <div class="my-auto ml-3 flex flex-column w-full">
            @if (paper) {
                <div>
                    <div class="font-semibold mb-1"><small>Research paper</small></div>
                    <div class="mb-1"><i>{{ paper.title[0] }}</i></div>
                    <p class="mb-3"> {{ paper.author[0].family }} et al., {{ paper['container-title'] }}, {{ paper['journal-issue']?.issue || '?' }}, {{ paper['published-print']?.['date-parts'][0][0] || '' }}</p>
                    <a [href]="paper.URL" target="_blank"><p-button icon="pi pi-arrow-right" label="Access the publication"/></a>
                </div>
            } @else {
                <p-skeleton width="100%" height="7rem" />
            }
        </div>
    </div>
  `
})
export class RandomPaperComponent {
  paper: any = null;
  isLoading = false;
  errorMessage = '';
  illustration='assets/images/landing/papers.svg';

  private readonly http = inject(HttpClient)

  // Helper to generate a deterministic hash based on the current date
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

  constructAPIcall() {
    const baseUrl = 'https://api.crossref.org/works';
    const query = 'cancer';
    const filters = `from-pub-date:${this.generateDynamicDateFilter()}`;
    const rows = 1; // Maximum number of papers to retrieve

    // Construct API URL
    return `${baseUrl}?query=${encodeURIComponent(query)}&facet=type-name:journal-article&filter=${filters}&rows=${rows}&sort=published&order=asc`;
  }

    public paper$ = this.http.get(this.constructAPIcall()).pipe(
        map((response: any) => {
        const papers = response.message.items;
        if (papers && papers.length > 0) {
            // Determine a paper based on today's date
            const index = this.getDateBasedIndex(papers.length);
            return papers[index];
        } else {
            this.errorMessage = 'No papers found for the given query.';
            return of()
        }
        }),
        catchError((error) => {
        this.errorMessage = 'An error occurred while fetching data.';
        console.error(error);
        return of(error)
        })
    );
}