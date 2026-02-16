import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { NovelsService } from '../../../../core/api/novels.service';
import { NovelCreate, NovelOut } from '../../../../core/models/novel.model';

@Component({
  selector: 'app-novel-list',
  templateUrl: './novel-list.component.html',
})
export class NovelListComponent implements OnInit {
  novels: NovelOut[] = [];
  loading = false;
  error: string | null = null;

  createOpen = false;
  form: NovelCreate = { name: '', source_lang: 'ko', target_lang: 'en' };

  constructor(private novelsApi: NovelsService, private router: Router) { }

  ngOnInit(): void {
    this.reload();
  }

  reload() {
    this.loading = true;
    this.error = null;
    this.novelsApi.list().subscribe({
      next: (data) => { this.novels = data; this.loading = false; },
      error: (err) => { this.error = err?.message || 'Failed to load novels'; this.loading = false; },
    });
  }

  open(n: NovelOut) {
    this.router.navigate(['/novels', n.id]);
  }

  toggleCreate() {
    this.createOpen = !this.createOpen;
    this.error = null;
  }

  create() {
    const name = this.form.name.trim();
    if (!name) return;

    this.loading = true;
    this.novelsApi.create({ ...this.form, name }).subscribe({
      next: (n) => {
        this.loading = false;
        this.createOpen = false;
        this.form.name = '';
        this.router.navigate(['/novels', n.id]);
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || err?.message || 'Create failed';
      },
    });
  }
}
