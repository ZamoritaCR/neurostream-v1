import Link from "next/link";

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  author: string;
  tags: string[];
}

// Blog posts metadata (in real app, this would come from CMS or markdown files)
const posts: BlogPost[] = [
  {
    slug: "introducing-dopamine-watch",
    title:
      "Introducing dopamine.watch: The Operating System for Neurodivergent Minds",
    excerpt:
      "Building a privacy-first digital toolkit designed specifically for ADHD and autistic users.",
    date: "2026-02-14",
    author: "Johan",
    tags: ["announcement", "product", "neurodiversity"],
  },
  {
    slug: "why-privacy-matters",
    title: "Why Privacy Matters for Neurodivergent Users",
    excerpt:
      "Discord's face scan requirement highlights why privacy-first platforms are essential.",
    date: "2026-02-14",
    author: "Johan",
    tags: ["privacy", "discord", "community"],
  },
];

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Link
            href="/"
            className="text-primary hover:text-primary-hover text-sm mb-4 inline-block"
          >
            &larr; Back to Home
          </Link>
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Blog
            </span>
          </h1>
          <p className="text-xl text-muted">
            Thoughts on building for neurodivergent minds
          </p>
        </div>
      </header>

      {/* Posts Grid */}
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="space-y-8">
          {posts.map((post) => (
            <Link
              key={post.slug}
              href={`/blog/${post.slug}`}
              className="block group"
            >
              <article className="p-6 bg-surface border border-border rounded-lg hover:border-primary transition-colors">
                <div className="flex items-center gap-3 text-sm text-muted mb-3">
                  <time dateTime={post.date}>
                    {new Date(post.date).toLocaleDateString("en-US", {
                      month: "long",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </time>
                  <span>&bull;</span>
                  <span>{post.author}</span>
                </div>

                <h2 className="text-2xl font-bold mb-3 group-hover:text-primary transition-colors">
                  {post.title}
                </h2>

                <p className="text-muted mb-4">{post.excerpt}</p>

                <div className="flex gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-surface-hover rounded-full text-xs text-muted"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </article>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
