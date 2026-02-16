import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ChaptersService } from '../../../../core/api/chapters.service';
import { NovelsService } from '../../../../core/api/novels.service';
import { ChapterListItem } from '../../../../core/models/chapter.model';
import { NovelOut } from '../../../../core/models/novel.model';

@Component({
  selector: 'app-novel-detail',
  templateUrl: './novel-detail.component.html',
})
export class NovelDetailComponent implements OnInit {
  novelId!: number;
  novel: NovelOut | null = null;
  chapters: ChapterListItem[] = [];
  loading = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private novelsApi: NovelsService,
    private chaptersApi: ChaptersService
  ) { }

  ngOnInit(): void {
    this.novelId = Number(this.route.snapshot.paramMap.get('novelId'));
    this.load();
  }

  load() {
    this.loading = true;
    this.error = null;

    this.novelsApi.get(this.novelId).subscribe({
      next: (n) => (this.novel = n),
      error: () => (this.error = 'Novel not found'),
    });

    this.chaptersApi.list(this.novelId).subscribe({
      next: (chs) => { this.chapters = chs; this.loading = false; },
      error: () => { this.error = 'Failed to load chapters'; this.loading = false; },
    });
  }

  read(ch: ChapterListItem) {
    this.router.navigate(['/reader', this.novelId, ch.chapter_no]);
  }
}
