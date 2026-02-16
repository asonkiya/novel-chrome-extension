import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { NovelCreate, NovelOut } from '../models/novel.model';

@Injectable({ providedIn: 'root' })
export class NovelsService {
  private base = environment.apiBaseUrl.replace(/\/+$/, '');

  constructor(private http: HttpClient) { }

  list() {
    return this.http.get<NovelOut[]>(`${this.base}/novels`);
  }

  create(payload: NovelCreate) {
    return this.http.post<NovelOut>(`${this.base}/novels`, payload);
  }

  get(novelId: number) {
    return this.http.get<NovelOut>(`${this.base}/novels/${novelId}`);
  }
}
