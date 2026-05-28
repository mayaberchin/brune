function ClassFilter({
  classes,
  selectedClassId,
  setSelectedClassId,
  showAll = true,
}) {
  return (
    <div className="class-filter-panel">
      <h2 className="h4">Courses</h2>

      {showAll && (
        <button
          type="button"
          className={selectedClassId === "all" ? "class-filter active" : "class-filter"}
          onClick={() => setSelectedClassId("all")}
        >
          All
        </button>
      )}

      {classes.map((classInfo) => (
        <button
          key={classInfo.class_id}
          type="button"
          className={
            selectedClassId === String(classInfo.class_id)
              ? "class-filter active"
              : "class-filter"
          }
          onClick={() => setSelectedClassId(String(classInfo.class_id))}
        >
          {classInfo.name}
        </button>
      ))}
    </div>
  );
}

function MobileClassFilter({
  classes,
  selectedClassId,
  setSelectedClassId,
  showAll = true,
}) {
  return (
    <details className="mobile-class-filter">
      <summary>Courses</summary>

      <ClassFilter
        classes={classes}
        selectedClassId={selectedClassId}
        setSelectedClassId={setSelectedClassId}
        showAll={showAll}
      />
    </details>
  );
}

export { MobileClassFilter };
export default ClassFilter;
