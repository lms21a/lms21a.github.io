import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getPosts, postUrl } from '../lib/posts';
import { site } from '../site';

export async function GET(context: APIContext) {
  return rss({
    title: `${site.author} — ${site.title}`,
    description: site.description,
    site: context.site!,
    // Feeds never expose drafts, even during a local draft preview.
    items: (await getPosts()).filter(post => !post.data.draft && post.data.date <= new Date()).map(post => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: postUrl(post),
      categories: post.data.tags,
      customData: post.data.updated ? `<updated>${post.data.updated.toISOString()}</updated>` : undefined,
    })),
    customData: '<language>en-us</language>',
  });
}
