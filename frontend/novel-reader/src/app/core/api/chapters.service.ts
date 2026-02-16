import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { ChapterListItem, ChapterOut } from '../models/chapter.model';

@Injectable({ providedIn: 'root' })
export class ChaptersService {
  private base = environment.apiBaseUrl.replace(/\/+$/, '');

  constructor(private http: HttpClient) { }

  list(novelId: number, limit = 500, offset = 0) {
    const params = new HttpParams().set('limit', limit).set('offset', offset);
    return this.http.get<ChapterListItem[]>(`${this.base}/novels/${novelId}/chapters`, { params });
  }

  getByNo(novelId: number, chapterNo: number) {
    return this.http.get<ChapterOut>(`${this.base}/novels/${novelId}/chapters/${chapterNo}`);
  }

  translate(chapterId: number) {
    return this.http.post<ChapterOut>(`${this.base}/chapters/${chapterId}/translate`, {});
  }

  format(chapterId: number) {
    return this.http.post<ChapterOut>(`${this.base}/chapters/${chapterId}/format`, {});
  }
}
