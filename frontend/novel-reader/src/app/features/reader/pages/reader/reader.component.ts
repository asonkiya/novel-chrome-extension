import { Component, HostListener, OnInit } from '@angular/core';
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

  private formatting = false;

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
      next: (ch) => {
        this.chapter = ch;
        this.loading = false;
      },
      error: () => {
        this.error = `Chapter ${this.chapterNo} not found`;
        this.loading = false;
      },
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

  onFormat() {
    if (!this.chapter?.id) return;
    if (this.formatting) return;

    this.formatting = true;
    this.error = null;

    this.chaptersApi.format(this.chapter.id).subscribe({
      next: (updated) => {
        this.chapter = updated;
        this.formatting = false;
      },
      error: (err) => {
        console.error(err);
        this.formatting = false;
        alert('Format failed (is it translated yet?)');
      },
    });
  }

  @HostListener('window:keydown', ['$event'])
  handleKeydown(e: KeyboardEvent) {
    const target = e.target as HTMLElement | null;
    const tag = target?.tagName?.toLowerCase();
    const isTyping =
      tag === 'input' ||
      tag === 'textarea' ||
      !!target?.isContentEditable;

    if (isTyping) return;
    if (e.repeat) return;

    // Left / k = prev
    if (e.key === 'ArrowLeft' || e.key === 'k' || e.key === 'K') {
      e.preventDefault();
      this.prev();
      return;
    }

    // Right / j = next
    if (e.key === 'ArrowRight' || e.key === 'j' || e.key === 'J') {
      e.preventDefault();
      this.next();
      return;
    }

    // f = format
    if (e.key === 'f' || e.key === 'F') {
      e.preventDefault();
      this.onFormat();
      return;
    }
  }
}
