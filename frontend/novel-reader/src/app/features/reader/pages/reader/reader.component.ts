import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ChaptersService } from '../../../../core/api/chapters.service';
import { ChapterOut } from '../../../../core/models/chapter.model';

@Component({
  selector: 'app-reader',
  templateUrl: './reader.component.html',
})
export class ReaderComponent implements OnInit {
  novelId!: number;
  chapterNo!: number;

  chapter: ChapterOut | null = null;
  loading = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chaptersApi: ChaptersService
  ) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe((pm) => {
      this.novelId = Number(pm.get('novelId'));
      this.chapterNo = Number(pm.get('chapterNo'));
      this.load();
    });
  }

  load() {
    this.loading = true;
    this.error = null;
    this.chapter = null;

    this.chaptersApi.getByNo(this.novelId, this.chapterNo).subscribe({
      next: (ch) => { this.chapter = ch; this.loading = false; },
      error: () => { this.error = `Chapter ${this.chapterNo} not found`; this.loading = false; },
    });
  }

  prev() {
    if (this.chapterNo <= 1) return;
    this.router.navigate(['/reader', this.novelId, this.chapterNo - 1]);
  }

  next() {
    this.router.navigate(['/reader', this.novelId, this.chapterNo + 1]);
  }

  translate() {
    if (!this.chapter) return;
    this.chaptersApi.translate(this.chapter.id).subscribe({
      next: (ch) => (this.chapter = ch),
      error: () => (this.error = 'Translate failed (check API key / logs)'),
    });
  }
}
