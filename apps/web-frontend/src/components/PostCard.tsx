type TextPost = { type: "text"; title?: string; body: string };
type CarouselPost = {
  type: "carousel";
  title?: string;
  slides: { caption: string }[];
};
type ArticlePost = {
  type: "article";
  title?: string;
  summary: string;
  wordCount?: number;
};
type PollPost = {
  type: "poll";
  question: string;
  options: string[];
  closesAt?: string;
};

type Post = TextPost | CarouselPost | ArticlePost | PollPost;

export default function PostCard(props: Post) {
  return (
    <article className="rounded-xl border p-4 space-y-2">
      {"title" in props && props.title ? (
        <h4 className="font-medium">{props.title}</h4>
      ) : null}

      {props.type === "text" && (
        <p className="text-sm text-gray-700 whitespace-pre-wrap">
          {props.body}
        </p>
      )}

      {props.type === "carousel" && (
        <div className="grid gap-2 sm:grid-cols-2">
          {props.slides.slice(0, 6).map((s, i) => (
            <div key={i} className="rounded-lg border p-3 text-sm bg-gray-50">
              <div
                className="mb-2 h-24 rounded bg-gray-200"
                aria-label="image placeholder"
              />
              <div className="text-gray-700">{s.caption}</div>
            </div>
          ))}
        </div>
      )}

      {props.type === "article" && (
        <div className="text-sm text-gray-700">
          <p className="mb-2">{props.summary}</p>
          {props.wordCount ? (
            <div className="text-xs text-gray-500">
              ~{props.wordCount} words
            </div>
          ) : null}
        </div>
      )}

      {props.type === "poll" && (
        <div className="text-sm">
          <div className="mb-2 font-medium">{props.question}</div>
          <ul className="space-y-1">
            {props.options.map((o, i) => (
              <li key={i} className="rounded border px-2 py-1">
                {o}
              </li>
            ))}
          </ul>
          {props.closesAt && (
            <div className="mt-2 text-xs text-gray-500">
              Closes: {props.closesAt}
            </div>
          )}
        </div>
      )}
    </article>
  );
}
