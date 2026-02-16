import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ReaderComponent } from './pages/reader/reader.component';

const routes: Routes = [
  { path: ':novelId/:chapterNo', component: ReaderComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReaderRoutingModule { }
