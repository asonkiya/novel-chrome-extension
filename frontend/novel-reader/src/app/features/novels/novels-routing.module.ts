import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { NovelListComponent } from './pages/novel-list/novel-list.component';
import { NovelDetailComponent } from './pages/novel-detail/novel-detail.component';

const routes: Routes = [
  { path: '', component: NovelListComponent },
  { path: ':novelId', component: NovelDetailComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class NovelsRoutingModule { }
