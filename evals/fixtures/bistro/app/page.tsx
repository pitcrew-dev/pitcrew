import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>Bistro</h1>
      <Link href="/reserve">Reserve a table</Link>
    </main>
  );
}
