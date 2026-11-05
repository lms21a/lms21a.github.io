import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'posts'>;

// Drafts can only be exposed by a local dev server, never by a static build.
export const previewingDrafts = import.meta.env.DEV && import.meta.env.MODE === 'drafts';

export async function getPosts() {
  const now = new Date();
  return (await getCollection('posts', ({ data }) =>
    previewingDrafts || (!data.draft && data.date <= now),
  )).sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf() || a.id.localeCompare(b.id));
}

export function readingTime(post: Post) {
  const words = `${post.data.description} ${post.body ?? ''}`.replace(/```[\s\S]*?```/g, '').trim().split(/\s+/).filter(Boolean).length;
  return `${Math.max(1, Math.ceil(words / 160))} min read`;
}

export function formatDate(date: Date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'long', day: 'numeric', year: 'numeric', timeZone: 'UTC',
  }).format(date);
}

export const postUrl = (post: Post) => `/writing/${post.id}/`;
