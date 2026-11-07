import { routing } from "../../i18n/routing";

export default function DefaultLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang={routing.defaultLocale}>
      <head>
        <meta httpEquiv="refresh" content={`0;url=/${routing.defaultLocale}/`} />
      </head>
      <body>{children}</body>
    </html>
  );
}
