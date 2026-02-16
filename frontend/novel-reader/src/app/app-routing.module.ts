import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'novels' },

  {
    path: 'novels',
    loadChildren: () =>
      import('./features/novels/novels.module').then((m) => m.NovelsModule),
  },

  {
    path: 'reader',
    loadChildren: () =>
      import('./features/reader/reader.module').then((m) => m.ReaderModule),
  },

  { path: '**', redirectTo: 'novels' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule { }
