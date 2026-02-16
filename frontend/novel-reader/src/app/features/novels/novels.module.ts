import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { NovelsRoutingModule } from './novels-routing.module';
import { NovelListComponent } from './pages/novel-list/novel-list.component';
import { NovelDetailComponent } from './pages/novel-detail/novel-detail.component';
import { FormsModule } from '@angular/forms';


@NgModule({
  declarations: [
    NovelListComponent,
    NovelDetailComponent
  ],
  imports: [
    CommonModule,
    NovelsRoutingModule,
    FormsModule
  ]
})
export class NovelsModule { }
